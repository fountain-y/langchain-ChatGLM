#encoding:utf-8
import argparse
import json
import os
import shutil
from typing import List, Optional
import urllib
import asyncio
import nltk
import pydantic
import uvicorn
from fastapi import Body, Request, FastAPI, File, Form, Query, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing_extensions import Annotated
from starlette.responses import RedirectResponse

from chains.local_doc_qa import LocalDocQA
from configs.model_config import (KB_ROOT_PATH, EMBEDDING_DEVICE,
                                  EMBEDDING_MODEL, NLTK_DATA_PATH,
                                  VECTOR_SEARCH_TOP_K, LLM_HISTORY_LEN, OPEN_CROSS_DOMAIN)
import models.shared as shared
from models.loader.args import parser
from models.loader import LoaderCheckPoint
import shutil
import argparse

from tqdm import tqdm

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

def validate_kb_name(knowledge_base_id: str) -> bool:
    # 检查是否包含预期外的字符或路径攻击关键字
    if "../" in knowledge_base_id:
        return False
    return True

def get_doc_path(local_doc_id: str):
    return os.path.join(get_kb_path(local_doc_id), "content")

def get_kb_path(local_doc_id: str):
    return os.path.join(KB_ROOT_PATH, local_doc_id)

def get_vs_path(local_doc_id: str):
    return os.path.join(get_kb_path(local_doc_id), "vector_store")

def upload_files(
        files: Annotated[
            List[UploadFile], File(description="Multiple files as UploadFile")
        ],
        knowledge_base_id: str = Form(..., description="Knowledge Base Name", example="kb1"),
):
    if not validate_kb_name(knowledge_base_id):
        return False

    saved_path = get_doc_path(knowledge_base_id)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    filelist = []
    for file in files:
        file_content = ''
        file_path = os.path.join(saved_path, file.filename)
        file_content = file.read()
        if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
            continue
        with open(file_path, "wb") as f:
            f.write(file_content)
        filelist.append(file_path)
    if filelist:
        vs_path = get_vs_path(knowledge_base_id)
        vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store(filelist, vs_path)
        if len(loaded_files):
            file_status = f"documents {', '.join([os.path.split(i)[-1] for i in loaded_files])} upload success"
            return BaseResponse(code=200, msg=file_status)
    file_status = f"documents {', '.join([os.path.split(i)[-1] for i in loaded_files])} upload fail"
    return BaseResponse(code=500, msg=file_status)

def init_filepath(knowledgeid):
    knowledge_path = get_kb_path(knowledgeid)
    tmpfile_path = os.path.join(get_doc_path(knowledgeid), "tmp_files")
    vector_store_path = os.path.join(knowledge_path, "vector_store")
    
    shutil.rmtree(tmpfile_path, ignore_errors=True)
    shutil.rmtree(vector_store_path, ignore_errors=True)
    
def arg_parser():
    args = argparse.ArgumentParser()
    args.add_argument("-k", "--knowledge_base_id", type=str, default="regulation")
    return args.parse_args()

if __name__ == '__main__':
    # change the knowledge_base_id to your own
    # the path of the knowledge_base_id is knowledge_base/{knowledge_base_id}
    args = arg_parser()
    
    knowledge_base_id = args.knowledge_base_id
    
    if not validate_kb_name(knowledge_base_id):
        assert False, "Invalid knowledge base name"

    saved_path = get_doc_path(knowledge_base_id)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    filelist = []
    
    init_filepath(knowledge_base_id)
    
    for filename in tqdm(os.listdir(saved_path)):
        file_content = ''
        file_path = os.path.join(saved_path, filename)
        if not os.path.isfile(file_path) or not file_path.endswith(".txt"):
            continue
        with open(file_path, "r") as f:
            file_content = f.read()
        if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
            continue
        filelist.append(file_path)
    
    vs_path = get_vs_path(knowledge_base_id)
    
    localdocqa = LocalDocQA()
    localdocqa.init_cfg()
    vs_path, loaded_files = localdocqa.init_knowledge_vector_store(filepath=filelist, vs_path=vs_path)
    print('kb init finish!')
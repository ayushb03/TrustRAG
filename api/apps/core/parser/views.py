#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:quincy qiang
@license: Apache Licence
@file: views.py
@time: 2024/06/13
@contact: yanqiangmiffy@gamil.com
@software: PyCharm
@description: coding..
"""
import re

import loguru
import magic
from fastapi import APIRouter
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from gomate.modules.document.chunk import TextChunker
from gomate.modules.document.docx_parser import DocxParser
from gomate.modules.document.excel_parser import ExcelParser
from gomate.modules.document.html_parser import HtmlParser
from gomate.modules.document.json_parser import JsonParser
from gomate.modules.document.pdf_parser_fast import PdfSimParser
from gomate.modules.document.ppt_parser import PptParser
from gomate.modules.document.txt_parser import TextParser

tc = TextChunker()
parse_router = APIRouter()


@parse_router.post("/parse/", response_model=None, summary="文件解析")
async def parser(file: UploadFile = File(...), chunk_size: int = 512):
    try:
        # 读取文件内容
        filename = file.filename
        content = await file.read()
        # bytes_io = BytesIO(content)
        # 检测文件类型
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(content)
        loguru.logger.info(filename, content, mime)
        if re.search(r"\.docx$", filename, re.IGNORECASE):
            parser = DocxParser()
        elif re.search(r"\.pdf$", filename, re.IGNORECASE):
            parser = PdfSimParser()
        elif re.search(r"\.xlsx?$", filename, re.IGNORECASE):
            parser = ExcelParser()
        elif re.search(r"\.pptx$", filename, re.IGNORECASE):
            parser = PptParser()
        elif re.search(r"\.(txt|md|py|js|java|c|cpp|h|php|go|ts|sh|cs|kt)$", filename, re.IGNORECASE):
            parser = TextParser()
        elif re.search(r"\.(htm|html)$", filename, re.IGNORECASE):
            parser = HtmlParser()
        elif re.search(r"\.doc$", filename, re.IGNORECASE):
            parser = DocxParser()
        elif re.search(r"\.json$", filename, re.IGNORECASE):
            parser = JsonParser()
        else:
            parser = DocxParser()
            raise NotImplementedError(
                "file type not supported yet(pdf, xlsx, doc, docx, txt supported)")
        contents = parser.parse(content)
        results = []
        if re.search(r"\.json$", filename, re.IGNORECASE):
            for section in contents:
                # chunks = tc.chunk_sentences(section['content'], chunk_size=chunk_size)
                if 'chunks' not in section:
                    chunks = tc.chunk_sentences(section['content'], chunk_size=chunk_size)
                    section['chunks'] = chunks
                else:
                    section['chunks'] = section['chunks']
                results.append(section)
        else:
            chunks = tc.chunk_sentences(contents, chunk_size=chunk_size)
            results.append(
                {
                    'source': '来源',
                    'title': '标题',
                    'date': '20241008',
                    'sec_num': 0,
                    'content': ''.join(chunks),
                    'chunks': chunks,
                }
            )

        loguru.logger.info(len(results))
        # 返回成功响应
        return JSONResponse(content=results, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

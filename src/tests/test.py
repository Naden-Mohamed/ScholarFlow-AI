from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from transformers import AutoTokenizer
from helpers.config import get_settings
from pathlib import Path

settings = get_settings()
source = Path("C:/Users/start/OneDrive/Desktop/ScholarFlow AI/src/Naden Mohamed Yasen - AI Engineer.pdf")

# --- Step 1: Configure pipeline ---
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False          # PDF has embedded text, OCR not needed
pipeline_options.do_table_structure = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# --- Step 2: Convert ---
print("Converting document...")
result = converter.convert(source)
doc = result.document
print(f"Document converted: {len(doc.pages)} pages")

# --- Step 3: Chunk ---
print("Chunking document...")
tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(settings.TOKENIZER_MODEL_ID),
    max_tokens=2000,
)
chunker = HybridChunker(tokenizer=tokenizer)

try:
    all_chunks = list(chunker.chunk(dl_doc=doc))  # materialize fully
except Exception as e:
    print(f"Chunking failed: {e}")
    all_chunks = []

print(f"Total chunks produced: {len(all_chunks)}")

# --- Step 4: Process chunks ---
processed_chunks = []

for idx, chunk in enumerate(all_chunks):
    contextualized_text = chunker.contextualize(chunk=chunk)

    meta = chunk.meta if hasattr(chunk, "meta") else {}
    headings = getattr(meta, "headings", []) or []
    doc_items = getattr(meta, "doc_items", []) or []

    page_numbers = []
    element_types = []
    for item in doc_items:
        for p in getattr(item, "prov", []) or []:
            page_no = getattr(p, "page_no", None)
            if page_no is not None:
                page_numbers.append(page_no)
        element_types.append(type(item).__name__)

    processed_chunks.append({
        "text": contextualized_text,
        "raw_text": chunk.text,
        "metadata": {
            "chunk_index": idx,
            "page_numbers": sorted(set(page_numbers)),
            "section_headings": headings,
            "element_types": list(set(element_types)),
            "token_count": tokenizer.count_tokens(contextualized_text),
            "has_table": any("Table" in t for t in element_types),
            "has_figure": any("Figure" in t or "Picture" in t for t in element_types),
        }
    })

# --- Quick inspection ---
for c in processed_chunks:
    print(f"\n--- Chunk {c['metadata']['chunk_index']} ---")
    print(f"Pages: {c['metadata']['page_numbers']}")
    print(f"Headings: {c['metadata']['section_headings']}")
    print(f"Types: {c['metadata']['element_types']}")
    print(f"Tokens: {c['metadata']['token_count']}")
    print(f"Text preview: {c['text'][:200]}")


# Stage preprocess failed for run 1, pages [54]: std::bad_alloc
# Stage preprocess failed for run 1, pages [55]: std::bad_alloc
# Document converted: 55 pages
# Chunking document...
# Token indices sequence length is longer than the specified maximum sequence length for this model (572 > 512). Running this sequence through the model will result in indexing errors
# Total chunks produced: 13

# --- Chunk 0 ---
# Pages: [1]
# Headings: ['Agent Tools & Interoperability with MCP']
# Types: ['DocItem']
# Tokens: 31
# Text preview: Agent Tools & Interoperability with MCP
# Authors: Mike Styer, Kanchana Patlolla,
# Madhuranjan Mohan, and Sal Diaz

# --- Chunk 1 ---
# Pages: [2]
# Headings: ['Acknowledgements']
# Types: ['DocItem']
# Tokens: 26
# Text preview: Acknowledgements
# Content contributors
# Antony Arul
# Ruben Gonzalez
# Che Liu
# Kimberly Milam
# Anant Nawalgaria
# Geir Sjurseth

# --- Chunk 2 ---
# Pages: [2]
# Headings: ['Curators and editors']
# Types: ['DocItem']
# Tokens: 20
# Text preview: Curators and editors
# Anant Nawalgaria
# Kanchana Patlolla
# Designer
# Michael Lanning
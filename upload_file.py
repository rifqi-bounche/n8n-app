import streamlit as st
from openai import OpenAI

# 🔑 API Key
client = OpenAI(api_key="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")

st.title("📂 Upload File Knowledge Base")

# Upload file via Streamlit
uploaded_file = st.file_uploader("Pilih file PDF untuk ditambahkan menjadi knowledge base", type=["pdf"])

if uploaded_file is not None:
    st.write("Nama file:", uploaded_file.name)

    # Simpan sementara ke memory & kirim ke OpenAI
    file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id="vs_68ae8dab9e20819198991855e92be9da",
        files=[uploaded_file]  # langsung pakai file-like object
    )

    st.success("✅ File berhasil dimasukkan ke vector store!")
    st.json({
        "status": file_batch.status,
        "file_count": file_batch.file_counts
    })

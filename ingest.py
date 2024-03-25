import xml.etree.ElementTree as ET

import boto3
import requests
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Setup Chrome Driver, may need to change based on system
service = Service("/usr/local/bin/chromedriver")
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service, options=options)

# Setup bedrock
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)


def extract_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        print(f"Failed to fetch sitemap: {response.status_code}")
        return []

    sitemap_content = response.content
    root = ET.fromstring(sitemap_content)

    # Extract the URLs from the sitemap
    urls = [
        elem.text
        for elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    ]

    return urls


def load_html_text(sitemap_urls):
    loader = SeleniumURLLoader(urls=sitemap_urls)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_documents(data)

    return texts


def embed_text(texts, save_loc):
    embeddings = BedrockEmbeddings(
        client=bedrock_runtime,
        region_name="us-east-1",
        model_id="amazon.titan-embed-text-v1",
    )

    # Split texts to batchs of 10, then merge each batch
    final_db = None
    for i in range(2000, len(texts), 10):
        # An array of i to i+10
        print(f"Getting docs from {i} to {i+10} of {len(texts)}")
        sample_texts = texts[i : i + 10]
        try:
            temp_db = FAISS.from_documents(sample_texts, embeddings)
        except Exception as e:
            print("Failed o well")
            continue

        if i == 0:
            final_db = temp_db

        if i > 0:
            final_db.merge_from(temp_db)

    final_db.save_local(save_loc)


def get_texts_from_well_arch_framework():
    # Site maps for the AWS Well-Architected Framework
    sitemap_url_list = [
        "https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/framework/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/sitemap.xml",
        "https://docs.aws.amazon.com/wellarchitected/latest/sustainability-pillar/sitemap.xml",
    ]

    # Get all links from the sitemaps
    full_sitemap_list = []
    for sitemap in sitemap_url_list:
        full_sitemap_list.extend(extract_urls_from_sitemap(sitemap))

    print(full_sitemap_list)
    texts = load_html_text(full_sitemap_list)
    return texts


def main() -> None:
    """
    Purpose:
        Ingest data into a a local db
    Args:
        N/A
    Returns:
        N/A
    """

    # get the raw html text
    texts = get_texts_from_well_arch_framework()

    # Save embeddings to local_index
    embed_text(texts, "local_index")


if __name__ == "__main__":
    main()

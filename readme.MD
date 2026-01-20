# 🏥 AI-Powered Serverless Healthcare Chatbot

## 📌 Project Overview
A cloud-native conversational assistant designed to automate patient intake and answer medical queries. This system uses a **custom Edge NLP engine** (Jaccard Similarity) running on **AWS Lambda** to perform "Smart Fallback" search on a mental health dataset, ensuring 100% uptime without external API dependencies.

## 🚀 Live Demo
[Click here to chat with the bot](https://maheshvg2002.github.io/aws-healthcare-chatbot/)

## 🏗 Architecture
* **Frontend:** Web Interface (Hosted on GitHub Pages) + Kommunicate.io
* **Core Logic:** AWS Lambda (Python 3.12)
* **NLP Engine:** Custom Jaccard Similarity Algorithm (Latency < 200ms)
* **Database:** Amazon DynamoDB (NoSQL) for Appointments & FAQs
* **Integration:** Amazon Lex V2

## ⚡ Key Features
* **Hybrid Flow:** Seamlessly switches between structured intents (Booking) and unstructured natural language queries.
* **Zero-Downtime NLP:** Replaced unstable external AI APIs with a local tokenization algorithm.
* **Smart Fallback:** Routes unrecognized queries to a knowledge base search automatically.

## 🛠 Setup & Installation
1. Clone the repo.
2. Run `data/upload_data.py` to hydrate the DynamoDB table.
3. Deploy `backend/lambda_function.py` to AWS Lambda.
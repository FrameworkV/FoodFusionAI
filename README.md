<div align="center">
  <a href="https://github.com/FrameworkV/FoodFusionAI">
    <img src="https://github.com/user-attachments/assets/8f6467ca-0239-401e-98ae-e802ae4b0700" alt="Logo" width="200" height="200">
  </a>

  <h3 align="center">FoodFusion AI</h3>

  <p align="center">
    Open Source groceries management with AI (LLMs).
    <br /><br />
    <a><strong>Give it a try:</strong></a>
    <br />
    
   [![Website](https://img.shields.io/badge/Website-Click_here-blue?style=for-the-badge)](https://zealous-bush-0277f6903.5.azurestaticapps.net/)
  </p>
</div>

<br>

> [!WARNING]
> This application is under active development. Errors might occur.
> 
> **Test the frontend locally** with the hosted backend following [this](DEVELOPMENT.md) guide.

> [!NOTE]
> The application relies on the Azure and Gemini **free tiers**, so we are limited to free offers (e.g. no VectorDB for RAG).
>
> **Cloud is expensive - so more features come with more users!** 

## Demo

TODO insert demo video

<br>

---

<br><br>

## 🌟 Features

- **User profile**: Consideration of preferences, diets and allergies
- **Automated shopping list**: Dynamic generation and customisation based on stocks and recipes
- **Recipes**: Suggestions based on current stocks, seasonal food, allergies and more 
- **Reminders**: Reminds you if food is about to expire

Availabe on the **web** (App release coming soon!)

[![Website](https://img.shields.io/badge/Website-1DBF73?style=flat&logo=internet-explorer&logoColor=white)](https://zealous-bush-0277f6903.5.azurestaticapps.net/)

<br><br>

## ⚙️ Tech stack

### 🧠 LLM
- **Model**: Gemini 1.5 Flash ![AI](https://img.shields.io/badge/AI-%2300BFFF.svg?&style=flat&logo=Artificial%20Intelligence&logoColor=white)

### 🖥️ Backend
  ![Architecture](./assets/architecture.drawio.png)

<br>

- **Python>=3.10**

  [![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3100/)
- **Frameworks**:

  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white)
  ![SQLModel](https://img.shields.io/badge/SQLModel-00833F?style=flat&logo=sqlmodel&logoColor=white)
  ![LangChain](https://img.shields.io/badge/LangChain-%230073e5.svg?&style=flat&logo=LangChain&logoColor=white)

- **Cloud Platform**:
    | Service | Purpose | |
    | ----------- | ----------- | ----------- |
    | **Azure Web App** | 	API & backend logic | ![Logos](https://skillicons.dev/icons?i=azure) |
    | **Azure CosmosDB** | LLM chat history storage	| ![Logos](https://skillicons.dev/icons?i=azure) |
    | **Azure SQL Database** | User & groceries table	| ![Logos](https://skillicons.dev/icons?i=azure) |
    
### 🛡️ Security

#### Secured API endpoints
All FastAPI endpoints are protected by security measures:
- **Authentication and authorisation**: Only authenticated users can access protected resources (OAuth2, JWT)
- **Timing Attacks protection**
- **DDoS and Brute Force protection**: Using rate limiting with Redis cache 

#### Protection of the user data

The user database is additionally protected by several layers of security:
- **Firewall**: The Azure database is configured by a firewall that only allows access from trusted IP addresses
- **Data encryption**: All data in the database is encrypted to ensure the highest level of data security

### 🎨 Frontend
Find anything related to the frontend here:

https://github.com/FrameworkV/FoodFusionAI-Website
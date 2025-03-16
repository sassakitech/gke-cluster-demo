# gke-cluster-demo

Este repositório contém um exemplo de infraestrutura como código (IaC) usando Terraform para provisionar um cluster Kubernetes (GKE) no Google Cloud Platform (GCP), além de uma aplicação Python simples containerizada e configurada para deploy no cluster usando Helm. Tudo será executado diretamente no Google Cloud Shell, sem necessidade de configuração local.

## Estrutura do Projeto

```
gke-cluster-demo/                     # Nome do repositório
├── terraform/                        # Código Terraform para provisionar a infraestrutura
│   ├── provider.tf                   # Configuração do provedor GCP
│   ├── network.tf                    # Configuração de rede e subnets
│   ├── gke.tf                        # Configuração do cluster Kubernetes
│   ├── outputs.tf                    # Outputs do Terraform
├── app/                              # Código da aplicação Python
│   ├── app.py                        # Aplicação Flask "Hello World"
│   ├── requirements.txt              # Dependências do Python
│   ├── Dockerfile                    # Dockerfile para containerizar a aplicação
│   ├── test_app.py                   # Testes da aplicação
├── helm/                             # Helm Chart para deploy no Kubernetes
│   ├── Chart.yaml                    # Definição do Helm Chart
│   ├── values.yaml                   # Valores configuráveis do Chart
│   ├── templates/                    # Templates Kubernetes
│   │   ├── deployment.yaml           # Deployment da aplicação
│   │   ├── service.yaml              # Service do tipo ClusterIP
│   │   ├── ingress.yaml              # Ingress para expor a aplicação
├── cloudbuild.yaml                   # Configuração do pipeline CI/CD no Cloud Build
├── README.md                         # Documentação do projeto
```

## Pré-requisitos

1. Google Cloud Shell: Acesse o Google Cloud Console e inicie o Cloud Shell.

2. Definir o Projeto Padrão:
```
gcloud config set project <id-do-projeto>
```
3. Caso não saiba o ID do projeto, liste os projetos disponíveis:
```
gcloud projects list
```

## Configuração Inicial

1. Clonar o Repositório
No Cloud Shell, clone o repositório:
```
git clone https://github.com/sassakitech/gke-cluster-demo.git
cd gke-cluster-demo
```

2. Ativar APIs Necessárias
Ative as APIs do GCP necessárias para o projeto:
```
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

3. Configurar o Projeto no Terraform
No arquivo `terraform/provider.tf`, substitua o valor `change-me` pelo ID do seu projeto:
``` terraform
provider "google" {
  project = "<id-do-projeto>"
  region  = "us-central1"
}
```
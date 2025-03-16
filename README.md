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

## Configuração inicial

1. Clonar o repositório
No Cloud Shell, clone o repositório:
```
git clone https://github.com/sassakitech/gke-cluster-demo.git
cd gke-cluster-demo
```

2. Ativar APIs necessárias 
Ative as APIs do GCP necessárias para o projeto:
```
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

3. Configurar o Projeto no Terraform
No arquivo `terraform/provider.tf`, substitua o valor `change-me` pelo ID do seu projeto:
```hcl
provider "google" {
  project = "change-me"
  region  = "us-central1"
}
```

## Provisionando a Infraestrutura com Terraform

1. Inicializar e aplicar o Terraform
Navegue até o diretório `terraform/` e execute os seguintes comandos:
```bash
cd terraform/

# Inicializar o Terraform
terraform init

# Verificar o plano de execução
terraform plan

# Aplicar as configurações
terraform apply
```

Isso criará:

- Uma rede e subnets.
- Um cluster GKE com dois nós em zonas diferentes.

## Configurando o GKE

1. Conectar ao Cluster
Após o provisionamento, configure o `kubectl` para se conectar ao cluster:
```
gcloud container clusters get-credentials my-cluster --zone us-central1
```

2. Criar um Namespace
Crie um namespace para a aplicação:
```
kubectl create namespace meu-namespace
```

## Configurando o repositório de Imagens Docker

1. Criar repositório no Artifact Registry
Crie um repositório para armazenar as imagens Docker:
```
gcloud artifacts repositories create hello-world \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositório de imagens Docker para a aplicação Hello World"
```

## Pipeline CI/CD com Cloud Build

O arquivo cloudbuild.yaml define um pipeline CI/CD que automatiza o processo de clone do repositório, análise de código, construção e push da imagem Docker, configuração do kubectl e deploy da aplicação no GKE usando Helm. Abaixo estão os passos resumidos:

### Passos da pipeline
1. Clone do Repositório:
Clona o repositório `gke-cluster-demo` do GitHub para o ambiente do Cloud Build.

2. Análise de Código:
Realiza análise estática do código Python usando`flake`,`pytest` e `bandit`. Os testes e verificações são executados, mas falhas não interrompem o pipeline.

3. Construção da Imagem Docker:
Constrói a imagem Docker da aplicação a partir do `Dockerfile` na pasta `app/`.

4. Push da Imagem Docker:
Envia a imagem Docker construída para o repositório no Artifact Registry.

5. Configuração do kubectl:
Configura o `kubectl` para se conectar ao cluster GKE provisionado.

6. Instalação e Execução do Helm:
Instala o Helm e faz o deploy da aplicação no cluster GKE usando o Helm Chart.

### Adicionando permissões ao Cloud Build
1. Conceda as permissões necessárias ao Cloud Build:
```
gcloud projects add-iam-policy-binding <id-do-projeto> \
  --member=serviceAccount:<numero-do-projeto>@cloudbuild.gserviceaccount.com \
  --role=roles/editor

gcloud projects add-iam-policy-binding <id-do-projeto> \
  --member=serviceAccount:<numero-do-projeto>@cloudbuild.gserviceaccount.com \
  --role=roles/storage.admin

gcloud projects add-iam-policy-binding <id-do-projeto> \
  --member=serviceAccount:<numero-do-projeto>@cloudbuild.gserviceaccount.com \
  --role=roles/cloudbuild.builds.editor
```

### Executando o CI/CD

Para executar o pipeline, use o seguinte comando no diretório raiz do repositório:
```
gcloud builds submit --config=cloudbuild.yaml .
```

### Detalhes adicionais

Substitutions:
- A variável `_IMAGE_TAG` define a tag da imagem Docker. Padrão como `latest`.

Timeout:
- O pipeline tem um timeout de 1200 segundos (20 minutos).

Logs e Debugging:
- O comando no Cloud Shell já imprime em sua saída os logs da execução do Cloud Build. Para mais detalhes, no console do GCP, acesse Cloud Build e veja em Histórico.

## Acesso à aplicação
Após o deploy, obtenha o IP público para acessar a aplicação:
```
kubectl get ingress -n meu-namespace
```

Acesse a aplicação no navegador: `http://<ip-do-ingress>:80`.

## Troubleshooting

1. Verificar Logs
Para verificar logs da aplicação:
```
kubectl logs -n meu-namespace -l app=hello-world
```

2. Rollback com Helm
Se necessário, faça rollback da aplicação no Cloud Shell:
```
helm rollback hello-world -n meu-namespace
```
Caso o Helm não esteja instalado, execute:
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

## Limpeza dos recursos

1. Desinstalar a aplicação
Desinstale o Helm Chart:
```
helm uninstall hello-world -n meu-namespace
```

2. Deletar o namespace
```
kubectl delete namespace meu-namespace
```

3. Destruir a infraestrutura com Terraform
Navegue até o diretório `terraform/` e destrua os recursos:
```
cd terraform/
terraform destroy
```

4. Limpar recursos do GCP
- Exclua o repositório no Artifact Registry.
- Remova os arquivos do Cloud Build no Cloud Storage.
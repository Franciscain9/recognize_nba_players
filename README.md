# recognize_nba_players

## Connect to the K8s on GCP

```
gcloud auth login

gcloud container clusters get-credentials cluster-nba-project --zone europe-west1-b --project qualified-sun-333022

```

## docker build

docker build -t nba-test .

docker build -t gcr.io/qualified-sun-333022/python-scraping:2.0 .

## docker run

docker run -d nba-test

## GKE K8S

Connect to the cluster

kubectl config set-context --current --namespace=scraping

kubectl apply -f your_file.yaml

Create K8s Secret

kubectl create secret generic gcp-sva-cred --from-file=dev-credentials.json

## PostgreSQL and ML Flow

kubectl config set-context --current --namespace=mlflow
kubectl create secret generic gcsfs-creds --from-file=./keyfile.json

### PostGreSQL DB

helm install mlf-db bitnami/postgresql --set postgresqlDatabase=mlflow_db --set postgresqlPassword=xxxx --set service.type=NodePort

### PostgreSQL port 5432 from within your cluster:

mlf-db-postgresql.mlflow.svc.cluster.local - Read/Write connection


### ML Flow Tracking Server

```

Project : 

docker build --tag gcr.io/qualified-sun-333022/mlflow-tracking-server:v1 --file dockerfile_mlflow_tracking .

docker push gcr.io/qualified-sun-333022/mlflow-tracking-server:v1 --file dockerfile_mlflow_tracking .

helm repo add mlflow-tracking https://artefactory-global.github.io/mlflow-tracking-server/

helm install mlf-ts mlflow-tracking/mlflow-tracking-server \
--set env.mlflowArtifactPath=gs://mlflow-nba-artifacts \
--set env.mlflowDBAddr=xxxx \
--set env.mlflowUser=xxxx \
--set env.mlflowPass=xxxx \
--set env.mlflowDBName=xxxx \
--set env.mlflowDBPort=5432 \
--set service.type=LoadBalancer \
--set image.repository=xxxxx/xxxxx/mlflow-tracking-server \
--set image.tag=v1

Options : --dry-run --debug --wait

```
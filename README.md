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
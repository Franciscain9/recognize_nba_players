# recognize_nba_players

# docker build
docker build -t nba-test .

# docker run

docker run -d nba-test

# K8S

Connect to the cluster

kubectl config set-context --current --namespace=scraping

kubectl apply -f your_file.yaml
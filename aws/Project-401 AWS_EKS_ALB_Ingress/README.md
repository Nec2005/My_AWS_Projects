# Project-401 : AWS LoadBalancer Controller (ALB) and Ingress with EKS

 AWS LoadBalancer Controller and Ingress with EKS.

## Outline

- Part 1 - Installing kubectl and eksctl on Amazon Linux 2

- Part 2 - Creating the Kubernetes Cluster on EKS

- Part 3 - Ingress and AWS LoadBalancer Controller (ALB)


## Part 1 - Installing kubectl and eksctl on Amazon Linux 2

### Install git, helm and kubectl

- Launch an AWS EC2 instance of Amazon Linux 2 AMI (type t2.micro) with security group allowing SSH.

- Install helm.

```bash
curl -sSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm version --short


### Install eksctl

- Download and extract the latest release of eksctl with the following command.

```bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
```

- Move the extracted binary to /usr/local/bin.

```bash
sudo mv /tmp/eksctl /usr/local/bin
```

- Test that your installation was successful with the following command.

```bash
eksctl version
```

## Part 2 - Creating the Kubernetes Cluster on EKS

- If needed create ssh-key with commnad `ssh-keygen -f ~/.ssh/id_rsa`

- Configure AWS credentials.

```bash
aws configure
```

- Create an EKS cluster via `eksctl`. It will take a while.

```bash

eksctl create cluster \
 --name mycluster \
 --version 1.21 \
 --region us-east-1 \
 --nodegroup-name my-nodes \
 --node-type t2.medium \
 --nodes 1 \
 --nodes-min 1 \
 --nodes-max 2 \
 --ssh-access \
 --ssh-public-key  ~/.ssh/id_rsa.pub \
 --managed

or 

eksctl create cluster --region us-east-1 --node-type t2.medium --nodes 1 --nodes-min 1 --nodes-max 2 --name mycluster

```


```bash
$ eksctl create cluster --help
```


## Part 3 - Ingress and AWS LoadBalancer Controller (ALB)

- Firstly, deploy the AWS Load Balancer Controller to our Amazon EKS cluster according to [AWS Load Balancer Controller user guide](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html)

- Verify that the controller is installed.

```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
```



### Application



The directory structure is as follows:

```bash
.
├── k8s
│   ├── account-deploy.yaml
│   ├── account-service.yaml
│   ├── inventory-deploy.yaml
│   ├── inventory-service.yaml
│   ├── shipping-deploy.yaml
│   ├── shipping-service.yaml
│   ├── storefront-deploy.yaml
│   └── storefront-service.yaml
```


- Create an `ingress.yaml` file.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-myshop
  annotations: 
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing 

    # Health Check Settings
    alb.ingress.kubernetes.io/healthcheck-protocol: HTTP 
    alb.ingress.kubernetes.io/healthcheck-port: traffic-port
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '15' 
    alb.ingress.kubernetes.io/healthcheck-timeout-seconds: '5' 
    alb.ingress.kubernetes.io/success-codes: '200'
    alb.ingress.kubernetes.io/healthy-threshold-count: '2'
    alb.ingress.kubernetes.io/unhealthy-threshold-count: '2'

spec:
  rules:
    - http:
        paths:
          - path: /account
            pathType: Prefix
            backend:
              service:
                name: account-service
                port: 
                  number: 80
          - path: /inventory
            pathType: Prefix
            backend:
              service:
                name: inventory-service
                port:
                  number: 80
          - path: /shipping
            pathType: Prefix
            backend:
              service:
                name: shipping-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: storefront-service
                port: 
                  number: 80


```

- Launch the aplication.

```bash
kubectl apply -f k8s
```

- List the ingress.

```bash
kubectl get ingress
```

Output:

```bash
NAME                 CLASS    HOSTS   ADDRESS                                                                 PORTS   AGE
ingress-myshop   <none>   *       k8s-default-ingressc-38a2e90a69-465630546.us-east-2.elb.amazonaws.com   80      89s
```


### Adding hostname and certificate to ALB.

- Return the http to https.

- Firstly, bind ingress address to an host name in the route53 service.

- Then update the ingress.yaml

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-myshop
  annotations: 
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing 

    # Health Check Settings
    alb.ingress.kubernetes.io/healthcheck-protocol: HTTP 
    alb.ingress.kubernetes.io/healthcheck-port: traffic-port
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '15' 
    alb.ingress.kubernetes.io/healthcheck-timeout-seconds: '5' 
    alb.ingress.kubernetes.io/success-codes: '200'
    alb.ingress.kubernetes.io/healthy-threshold-count: '2'
    alb.ingress.kubernetes.io/unhealthy-threshold-count: '2'
    # To use certificate add annotations below.
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:00008888099:certificate/dae75cd6-8d82-420c-bed1-1ea132ec3d37
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'

spec:
  rules:
    - host: mycloudworld.co.uk
      http:
        paths:
          - path: /account
            pathType: Prefix
            backend:
              service:
                name: account-service
                port: 
                  number: 80
          - path: /inventory
            pathType: Prefix
            backend:
              service:
                name: inventory-service
                port:
                  number: 80
          - path: /shipping
            pathType: Prefix
            backend:
              service:
                name: shipping-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: storefront-service
                port: 
                  number: 80```

- Update the ingress.

```bash
kubectl apply -f ingress.yaml
```


Output:

```bash
NAME                 CLASS    HOSTS                     ADDRESS                                                                  PORTS   AGE
ingress-myshop   <none>   mycloudworld.co.uk   k8s-default-ingressc-38a2e90a69-1914587084.us-east-1.elb.amazonaws.com   80      16m
```

- Try to reach web page as http. `http://mycloudworld.co.uk`.

- Delete the cluster

```bash
$ eksctl get cluster
NAME            REGION
mycluster       us-east-2
$ eksctl delete cluster mycluster
```
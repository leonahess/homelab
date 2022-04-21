create db secret:
```
kubectl create secret generic nextcloud-db-secret \
    --from-literal=MYSQL_ROOT_PASSWORD=rootPassw0rd1 \
    --from-literal=MYSQL_USER=nextcloud \
    --from-literal=MYSQL_PASSWORD=passw0rd1
```

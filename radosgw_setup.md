Adapted from here: https://base64.co.za/enable-amazon-s3-interface/

On Node 1
```
# Create Keyring
ceph-authtool --create-keyring /etc/ceph/ceph.client.radosgw.keyring

# Generate Keys and add to Keyring
ceph-authtool /etc/ceph/ceph.client.radosgw.keyring -n client.radosgw.tinyprox1 --gen-key
ceph-authtool /etc/ceph/ceph.client.radosgw.keyring -n client.radosgw.tinyprox2 --gen-key
ceph-authtool /etc/ceph/ceph.client.radosgw.keyring -n client.radosgw.tinyprox3 --gen-key

# Add Capabilities  to keys
ceph-authtool -n client.radosgw.tinyprox1 --cap osd 'allow rwx' --cap mon 'allow rwx' /etc/ceph/ceph.client.radosgw.keyring
ceph-authtool -n client.radosgw.tinyprox2 --cap osd 'allow rwx' --cap mon 'allow rwx' /etc/ceph/ceph.client.radosgw.keyring
ceph-authtool -n client.radosgw.tinyprox3 --cap osd 'allow rwx' --cap mon 'allow rwx' /etc/ceph/ceph.client.radosgw.keyring

# Add Keys to Ceph Cluster
ceph -k /etc/ceph/ceph.client.admin.keyring auth add client.radosgw.tinyprox1 -i /etc/ceph/ceph.client.radosgw.keyring
ceph -k /etc/ceph/ceph.client.admin.keyring auth add client.radosgw.tinyprox2 -i /etc/ceph/ceph.client.radosgw.keyring
ceph -k /etc/ceph/ceph.client.admin.keyring auth add client.radosgw.tinyprox3 -i /etc/ceph/ceph.client.radosgw.keyring

# Copy Keyring to /etc/pve/priv
cp /etc/ceph/ceph.client.radosgw.keyring /etc/pve/priv
```

Edit `/etc/ceph/ceph.conf`
```
[client.radosgw.tinyprox1]
        host = tinyprox1
        keyring = /etc/pve/priv/ceph.client.radosgw.keyring
        log file = /var/log/ceph/client.radosgw.$host.log
        rgw_dns_name = s3.leona.pink

[client.radosgw.tinyprox2]
        host = tinyprox2
        keyring = /etc/pve/priv/ceph.client.radosgw.keyring
        log file = /var/log/ceph/client.radosgw.$host.log
        rgw_dns_name = s3.leona.pink

[client.radosgw.tinyprox3]
        host = tinyprox3
        keyring = /etc/pve/priv/ceph.client.radosgw.keyring
        log file = /var/log/ceph/client.rados.$host.log
        rgw_dns_name = s3.leona.pink
```

On each Node
```
apt install radosgw
systemctl start ceph-radosgw@radosgw.tinyprox1
```

Enable stuff
```
ceph osd pool application enable .rgw.root rgw
ceph osd pool application enable default.rgw.control rgw
ceph osd pool application enable default.rgw.log rgw
```

Create admin user and save acces/priv key
```
radosgw-admin user create --uid=testuser --display-name="Test User" --email=test.user@example.net
```

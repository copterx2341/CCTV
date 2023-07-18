import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

#Store Data to influx
def write_data(bucket, CCTV, field, org, token, url, count):
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = influxdb_client.Point("CCTV").tag("location", CCTV).field(field, count)
    write_api.write(bucket=bucket, org=org, record=data)



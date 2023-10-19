import psutil
import boto3
import datetime
from decimal import Decimal


def get_pc_stats():
    """Returns a dictionary of PC stats."""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pc_stats = {
        "PCID": "bharatsesham-pc",
        "Timestamp": current_time,
        "cpu_usage": Decimal(str(psutil.cpu_percent())),
        "ram_usage": Decimal(str(psutil.virtual_memory().percent)),
        "disk_usage": Decimal(str(psutil.disk_usage("/").percent)),
        "network_traffic": Decimal(str(psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv)),
        # "gpu_usage": psutil.gpu_percent(),
        # "fan_speed": psutil.sensors_fans()[0].current,
        # "temperature": psutil.sensors_temperatures()[0].current
    }
    return pc_stats


def write_pc_stats_to_dynamodb(pc_stats):
    """Writes the PC stats to AWS DynamoDB."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PCTStats')
    table.put_item(Item=pc_stats)

if __name__ == '__main__':
    pc_stats = get_pc_stats()
    print(pc_stats)
    write_pc_stats_to_dynamodb(pc_stats)


import psutil
import boto3
import datetime
from decimal import Decimal
import GPUtil



def get_pc_stats():
    """Returns a dictionary of PC stats."""
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Fetch GPU data
    GPUs = GPUtil.getGPUs()
    gpu = GPUs[0] if GPUs else None

    pc_stats = {
        "PCID": "bharatsesham-pc",
        "Timestamp": current_time,
        "Timestamp": current_time,
        "cpu_usage": Decimal(format(psutil.cpu_percent(), '.1f')),
        "ram_usage": Decimal(format(psutil.virtual_memory().percent, '.1f')),
        "disk_usage": Decimal(format(psutil.disk_usage("/").percent, '.1f')),
        "network_traffic": Decimal(format(psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv, '.1f')),
        "gpu_usage": Decimal(format(gpu.load * 100, '.1f')) if gpu else None,
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


import sys
import csv
from tqdm import tqdm
sys.path.append("../../")

from api import get_username, get_project_num

with open('users.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["project_id", "username", "projectNum"])

num = 0
for i in tqdm(range(997067481, 276751787, -1)):
  with open('users.csv', 'a', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      username = get_username(i)

      if not username:
        continue

      project_num = get_project_num(username)

      if not project_num:
        continue

      if project_num > 19:
        num += 1
        writer.writerow([i, username, project_num])
        print(num)

    
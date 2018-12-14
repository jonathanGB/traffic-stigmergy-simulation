import matplotlib.pyplot as plt
import os
import json
import numpy as np

# gather all JSON filenames
json_filenames = []
for file in os.listdir("stats"):
    if file.endswith(".json"):
      json_filenames.append(file)

json_filenames.sort(reverse=True)
# read all JSON data
n = len(json_filenames)
data = []
for json_filename in json_filenames:
  with open('stats/{}'.format(json_filename)) as f:
    data.append(json.load(f))

# draw histogram charts for prop_delays & delay_times
for category in ["prop_delays", "delay_times"]:
  plt.figure(figsize=(30,20)).suptitle(category, fontsize=16)
  ctr = 1

  for row_idx, output in enumerate(data):
    for day in range(5):
      subplot = plt.subplot(n, 5, ctr)
      if row_idx == 0:
        subplot.set_title("Day {}".format(day))

      plt.hist(output[str(day)]['cars'][category], label=json_filenames[row_idx].split('.json')[0])
      plt.legend()
      ctr += 1

  plt.savefig(category + ".png")

# draw horizontal bar charts for total travel times
plt.figure(figsize=(30,20)).suptitle("Total time", fontsize=16)
width = 0.35
for day in range(5):
  plt.subplot(5, 1, day+1).set_title("Day {}".format(day))
  travel_sums = []
  delay_sums = []
  
  for indx, output in enumerate(data):
    day_indx = str(day)
    total_times = np.array([output[day_indx]['cars']['delay_times'], output[day_indx]['cars']['travel_times']])
    delay_sum, travel_sum = total_times.sum(axis=1)
    
    travel_sums.append(travel_sum)
    delay_sums.append(delay_sum)

    print(json_filenames[indx], travel_sum)

  print()
  ind = np.arange(len(data))

  p1 = plt.barh(ind, travel_sums, width, label="Travel time sum")
  p2 = plt.barh(ind, delay_sums, width, left=travel_sums, label="Delay time sum")
  plt.legend()

  plt.gca().set_yticks(ind)
  plt.gca().set_yticklabels(map(lambda filename: filename.split(".json")[0], json_filenames))
  plt.xlim(150000, 270000)

plt.savefig("total_travel.png")
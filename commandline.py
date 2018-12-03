import argparse

def probability_float(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
      raise argparse.ArgumentTypeError("{} not in range [0.0, 1.0]".format(x))
    
    return x

def non_negative_float(x):
  x = float(x)
  if x < 0.0:
    raise argparse.ArgumentTypeError("{} should be non-negative".format(x))

  return x

"""
This is where we parse the command-line arguments.
We return a dictionary representing the key-value pairs that `main.py` requires to launch the simulation.
"""
def parse():
  parser = argparse.ArgumentParser(description='Run the traffic simulation')
  
  parser.add_argument('strategy', type=str, help='the name of the traffic strategy to run (see traffic.py)')
  parser.add_argument('--network', type=str, default="network1.txt", help="name of the network file (assuming it is in the `networks/` folder)")
  parser.add_argument('--num', type=int, help="Specify a number of robots to run")
  parser.add_argument('--until', type=int, help="Run the simulation for a maximum amount of time")
  parser.add_argument('--omega', type=probability_float, default=0.5, help="Specify the proportion of long-term vs short-term stigmergy in case2")
  parser.add_argument('--range', type=non_negative_float, default=1.0, help="Range of visibility for short-term stigmergy")
  parser.add_argument('--alpha', type=non_negative_float, default=0.48, help="Specify the alpha parameter in the anticipatory heuristic")
  parser.add_argument('--beta', type=probability_float, default=2.48, help="Specify the beta parameter in the anticipatory heuristic")
  parser.add_argument('--perc', type=probability_float, default=0.5, help="Specify the congestion criteria (percent allocated) in anticipatory stigmergy with allocation")


  args = vars(parser.parse_args())

  return {
    "strategy": args["strategy"],
    "network": "networks/" + args["network"],
    "until": args["until"],
    "range": args["range"],
    "param": {
      "num": args["num"],
      "omega": args["omega"],
      "alpha": args["alpha"],
      "beta": args["beta"],
      "perc": args["perc"]
    }
  }
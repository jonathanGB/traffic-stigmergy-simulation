import argparse

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

  args = vars(parser.parse_args())

  return {
    "strategy": args["strategy"],
    "network": "networks/" + args["network"],
    "until": args["until"],
    "param": {
      "num": args["num"]
    }
  }
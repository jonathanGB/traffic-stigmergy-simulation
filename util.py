"""
Generator function that simply returns a new ID, when requested.
"""
def generate_id():
  id = 0
  while True:
    yield id
    id += 1
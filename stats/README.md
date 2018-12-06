# How to gather stats with NYC traffic flow?

I added a new command-line argument. The first one defines the traffic flow, and the second one defines the strategies used by the cars.

Simulations now gather data, and save the data as a JSON file once the simulation is done in the `stats/` directory. You might find the flag `--output-file=<file_name.json>` useful (automatically prepends `stats/`). A brief look at the other command-line args is useful too.

We can also provide a special value for the 2nd argument, which is "all". If you give "all" (as done below), 6 simulations will be run in parallel (case0-case5). When running "all", the simulations will output the separate JSON files to their corresponding strategies' names (`case0.json` for instance). The flag `--output-file` is ignored.

```
python3 main.py nyc_weekday all --network manhattan_normal.txt --num=5
```

Now that we have gathered some JSON files, what should we do with it? For now, we can run

```
python3 stats_visualizer.py
```

which generates charts from all JSON files that are direct children of the `stats/` directory (it ignores recursive levels). So, if you want to generate other charts, you should look at `stats_visualizer.py`. If you want to see what data is gathered and outputed, you should look at `monitory.py`, especially the `register*` methods and the final `output_stats` method.

If some newly generated JSON files look interesting, I would suggest creating a directory under `stats/` and moving the desired files there. JSON files directly under `stats/` are ignored by git (see the folder's `.gitignore`), but this does not apply to JSON files in children folders. As well, the files directly under `stats/` have more chance of being overwritten (if you run a new simulation). 
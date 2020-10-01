import sys, os
import pickle

# Prepare an empty set of target objects
targets = set()

# For each item in command line...
for arg in sys.argv[1:]:

  # For each file, recursively...
  for root, dirs, files in os.walk(arg):
    print(root)

    for file in files:

      # Ignore file if not *.xml
      if not file.endswith('.xml'): continue

      # Read the file as a list of strings
      filename = os.path.join(root, file)
      with open(filename) as f:
        recs = f.readlines()

      # Find the beginning of a Target_Identification object
      for j,rec0 in enumerate(recs):
        if '<Target_Identification>' not in rec0: continue

        # Search forward for the end of this Target_Identification object
        for k,rec1 in enumerate(recs[j:]):
            if '</Target_Identification>' in rec1: break

        # Save the target XML in the set. This keeps only unique entries
        entry = recs[j:j+k+1]
        targets.add(tuple(entry)) # convert to tuple; lists are not hashable

# Convert to a list and sort
targets = list(targets)
targets.sort()

# Save as a pickle file for future examination
# with open('all_targets.pickle', 'w') as f:
#     pickle.dump(targets,f)

# Print the target objects
for target in targets:
    for rec in target:
        print(rec.rstrip())     # don't print trailing \r\n


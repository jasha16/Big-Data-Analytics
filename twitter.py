import networkx as nx
from networkx.classes.digraph import DiGraph
from networkx.convert_matrix import from_pandas_edgelist
import tweepy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import graphviz

def find_followers(u_id):
    followers = []

    try:

        follower_cursors = tweepy.Cursor(api.get_followers, user_id=u_id)

        for friend in follower_cursors.items(100):
            followers.append(friend.id)

        return followers
    except BaseException as e:
        print("Error!")


def generate_network(list_mentions):
  DG=nx.DiGraph()
  for l in list_mentions:
#    print(len(l), l)
    if len(l)<2: continue
    for n in l[1:]:
      if not DG.has_edge(l[0],n):
        DG.add_edge(l[0],n, weight=1.0 )
      else:
        DG[l[0]][n]['weight']+=1.0
  return DG

def in_degree_freq(G):
  #get all nodes in G
  nodes = G.nodes()
  
  #get the in degrees of nodes in G
  in_degree = dict(G.in_degree())

  #get only the degrees for nodes
  degrees = [in_degree.get(k) for k in nodes]

  #get the maximum in degree
  degree_max = max(degrees) + 1

  #update frequencies
  frequency = [ 0 for d in range(degree_max)]
  for d in degrees:
      frequency[d] += 1
  return frequency


consumer_key = '5wpCiuYDikv1NIh78rLQ1l7e5'
consumer_secret = 'hCdnEgvBYd65BOTLuqVWEYfhZIlWorWjitDwUyPQmQVRrLPJuY'
access_token = '1164432745520607232-tSidnTWwJYUHZiN1w6uJPAcqIDAl1k'
access_secret = 'KuAnaZ1sEHsW64aTViFIKULbxkGftRJ9M4koZAdlrOA1u'


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

#Find all followers needed to create the graph and save them to a csv.
#After running this once I have commented it out so the code doesnt depend on twitter rates
"""
uni = api.get_user(screen_name='freyahyness')

uni_followers = find_followers(uni.id)

df = pd.DataFrame(columns=['source','target'])
df['target'] = uni_followers
df['source'] = uni.id

#Get followers of university twitter followers

remaining = len(uni_followers)

for f in uni_followers:
    followers = find_followers(f)

    temp = pd.DataFrame(columns=['source','target'])
    temp['target'] = followers
    temp['source'] = f

    df = df.append(temp)

    df.to_csv("temp.csv")

    remaining -= 1
    print("Remaining: ",remaining)

df.to_csv("f.csv")
"""

fi = pd.read_csv("f.csv")

G = DiGraph(fi)
pos = pos = nx.spring_layout(G)

G_cut = nx.k_core(G, 7) #Exclude nodes with degree less than 2

f, ax = plt.subplots(figsize=(10, 10))
plt.style.use('ggplot')
nodes = nx.draw_networkx_nodes(G_cut, pos, alpha=0.8)
nodes.set_edgecolor('k')
nx.draw_networkx_edges(G_cut, pos, width=0.1, alpha=0.5)
plt.savefig("network.png")
plt.show()

frequency = np.array(in_degree_freq(G))

#calculate probabilities from frequency
frequency = frequency / frequency.sum()
degrees = range(len(frequency))

#plot on a logarithmic scale
plt.figure(figsize=(12, 8)) 
plt.loglog(range(len(frequency)), frequency, 'go-', label='in-degree')

plt.title("In-degree distribution")
plt.xlabel('In-degree (k)')
plt.ylabel('Probability P(k)')
plt.savefig("Probability.png")
plt.show()
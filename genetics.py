#!/usr/bin/env python3

import random
import math

"""A genome is a dictionary with keys as gene names, and with values as tuples of equally probable gene values.

e.g.
  genome = {"eyeColor" : ("blue","brown","hazel"),
            "height" : tuple(range(100,220,1)),
            "earLobes" : ("attached", "unattached")}

  note: This version of genetics does not have the concept of dominant/recessive genes.  ie, genotype==phenotype
  """


def roll(genome, random=random):
    """Randomly produce a set of genes based on the given genome."""
    return { key : random.choice(values) for (key,values) in genome.items()}

def cross(a, b, random=random):
    """Create a new set of genes.  Each gene is randomly selected from one of the parents."""
    return { key : random.choice([a,b])[key] for key in a.keys() }

def roulette_index(n, random=random):
    """Randomly choose an index from 0...n-1.  Choice has a weight of (index+1)."""
    rouletteValue = random.randint(0, n * (n-1) // 2)
    return math.ceil(-0.5 + math.sqrt(0.25 + 2 * rouletteValue))

def roulette(population, random=random):
    """Randomly select an individual from the population, weighted by (index+1)."""
    return population[roulette_index(len(population), random)]

def mutate(a, genome, keyProbability=None, random=random):
    """Randomly change each gene with probability keyProbability.

    Mutated genes are selected using roulette probability, weighted by proximity to the original gene.
    """
    if keyProbability==None:
      keyProbability = 1 / len(a.keys())
    for key in a.keys():
      if (random.random() <= keyProbability):
        originalValue = a[key]
        L = list(genome[key])
        try:
          L1 = L[:L.index(originalValue)]
        except ValueError:
          a[key] = random.choice(genome[key])
          return
        L.reverse()
        L2 = L[:L.index(originalValue)]
        if (random.random() < (len(L1)/(len(L1)+len(L2)))):
          L = L1
        else:
          L = L2
        a[key] = roulette(L)
    
def equals(a,b):
    """Return true iff each gene in a is identical in b (and vice versa)"""
    if (a==b):
      return True
    if (len(a) != len(b)):
      return False
    for key in a.keys():
      if a[key] != b[key]:
        return False
    return True 

class Population:
  """Encapsulate a set of individuals that can be evolved according to a scoring function."""

  def __init__(self, genome, scoringFunction, random=random):
    """Initialize the parameters for the population."""
    self.population = [] # a list of (indiviudal, score) tuples
    self.genome = genome
    self.scoringFunction = scoringFunction
    self.isSorted = True
    self.random = random

  def sort(self):
    """Sort the population by increasing score."""
    if self.isSorted:
      return
    self.population.sort(key = lambda r:r[1])  # ascending order, by score
    self.isSorted = True

  def score(self, individual):
    """Calculate the score for the given individual."""
    return (individual, self.scoringFunction(individual))

  def addRandomIndividuals(self, n):
    """Add n new random individuals to the population."""
    for i in range(n):
      self.addIndividual(roll(self.genome, self.random))

  def addIndividual(self, individual, score=None):
    """Add a single individual to the population."""
    if score:
      newMember = (individual, score)
    else:
      newMember = self.score(individual)
    self.population.append(newMember)
    self.isSorted = False

  def __len__(self):
    """Return the number of individuals in the population."""
    return len(self.population)

  def __contains__(self, individual):
    """Return true if the given individual exists in the population."""
    for member in self.population:
      if equals(member[0], individual):
        return True
    return False

  def copyPopulationFrom(self, other):
    """Duplicate another population."""
    self.population = other.population
    self.isSorted = other.isSorted

  def evolve(self, elitism=1, mutation=None):
    """Create a new generation of individuals using cross breeding, mutation and elitism."""
    self.sort()
    newPopulation = Population(self.genome, self.scoringFunction, self.random)
    for elite in self.population[-elitism:]:
      newPopulation.addIndividual(*elite)
    while len(newPopulation) < self.__len__():
      a = roulette(self.population, self.random)[0]
      b = roulette(self.population, self.random)[0]
      while (equals(a,b)):
        b = roulette(self.population, self.random)[0]
      c = cross(a,b)
      if (self.random.random() < mutation):
        mutate(c, self.genome, mutation, self.random)
      if not (c in newPopulation or self.__contains__(c)):
        newPopulation.addIndividual(c)
    self.copyPopulationFrom(newPopulation)

def frange(n, stop=None, step=1):
  """Generate values from n to stop (not including stop), incrementing by step.

  If stop is not supplied, generatve values from 0 to n (not including n)."""
  if step==0:
    return
  if stop==None:
    a = 0
    b = n
  else:
    a = n
    b = stop
  if step > 0:
    done = lambda x, y: (x>=y)
  else:
    done = lambda x, y: (x<=y)
  while not done(a,b):
    yield a;
    a += step
  return
      
def demo_score(i):
    """Score an individual by fit to ax^2+bx+c = e^x in the range [0,1]"""
    a = i["a"]
    b = i["b"]
    c = i["c"]
    return -sum([(lambda d:d*d)(a*x*x+b*x+c-math.exp(x)) for x in frange(0,1,0.001)])/1000

def demo_main():
    """Evolve an individual to maximize demo_score."""
    randomizer = random.Random()
    randomizer.seed(0)
    genome = { 
        "a": tuple(frange(-10,10,0.0001)), 
        "b": tuple(frange(-10,10,0.0001)), 
        "c": tuple(frange(-10,10,0.0001))}

    population = Population(genome,demo_score,randomizer)
#    population.addIndividual({"a":0.817, "b":0.886, "c":1.001})
    population.addRandomIndividuals(100)
    generation=0
    population.sort()
    for generation in range(1000):
      population.sort()
      if (generation % 50 == 0):
        print("gen %.3d: %s" % (generation, population.population[-1]))
        print("gen %.3d: %s" % (generation, population.population[-2]))
        print("gen %.3d: %s" % (generation, population.population[-3]))
        print()
      population.evolve(mutation=0.20, elitism=2)

    population.sort()
    print()
    print("gen %.3d: %s" % (generation, population.population[-1]))
    
    

if __name__=='__main__':
    demo_main()

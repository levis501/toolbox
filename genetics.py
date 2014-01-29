#!/usr/bin/env python3

import random
import math

"""A genome is a dictionary with keys as gene names, and with values as a sequence of equally probable gene values.

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
    If a gene is selected for mutation, there is a equal probability that the mutation will be before
    or after the original gene's value in the genome.  The new gene is then selected using roulette
    probability, sorted by proximity to the original gene.
    """
    if keyProbability==None:
      keyProbability = 1 / len(a.keys())
    for key in a.keys():
      if (random.random() <= keyProbability):
        # perform the following for each gene randomly selected for mutation
        originalValue = a[key]
        originalIndex = genome[key].index(originalValue)
        delta = roulette_index(len(genome[key]), random)
        if random.random() < 0.5:
          newIndex = (originalIndex + delta) % len(genome[key])
        else:
          newIndex = (originalIndex - delta) % len(genome[key])
        a[key] = genome[key][newIndex]
    
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
    self.individuals = set()
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
    for i in range(n):  # @UnusedVariable
      self.addIndividual(roll(self.genome, self.random))

  def addIndividual(self, individual, score=None):
    """Add a single individual to the population."""
    if score:
      newMember = (individual, score)
    else:
      newMember = self.score(individual)
    self.population.append(newMember)
    self.individuals.add(self.hash(individual))
    self.isSorted = False

  def __len__(self):
    """Return the number of individuals in the population."""
    return len(self.population)

  def hash(self, individual):
    return tuple(sorted(individual.items()))

  def __contains__(self, individual):
    """Return true if the given individual exists in the population."""
    return self.hash(individual) in self.individuals

  def copyPopulationFrom(self, other):
    """Duplicate another population."""
    self.population = list(other.population)
    self.individuals = set(other.individuals)
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


def frange(a, b, step):
  while a < b:
    yield a
    a += step
    

class Seq:
  def __init__(self, f, finv, a, b, length):
    self.f = f
    self.finv = finv
    self.a = a
    self.b = b
    self.length = length
    self.increment = (b-a)/(length-1)
  def __len__(self):
    return self.length
  def __getitem__(self, i):
    if type(i) != slice:
      x = self.a + i * self.increment
      return self.f(x)
    (start, stop, step) = i.indices(self.length)
    a = self.a + start * self.increment
    if start > stop:
      length = (start - stop - 1) // -step + 1
    else:
      length = (stop - start - 1) // step + 1
    if length <= 0:
      return []
    b = a + (length-1)*step * self.increment
    return Seq(self.f,self.finv,a,b,length)
  def __iter__(self):
    for i in range(0,self.length):
      yield self[i]
    return
  def reverse(self):
    a = self.b
    b = self.a
    self.a = a
    self.b = b
    self.increment = -self.increment
#   def __setitem__(self, key, value):
#   def __delitem__(self, key):
  def index(self, y):
    x = self.finv(y)
    i = round((x-self.a) / self.increment)
    if i<0 or i>=self.length:
      raise ValueError
    return i
    

def demo_score(i):
    """Score an individual by fit to ax^2+bx+c = e^x in the range [0,1]"""
    a = i["a"]
    b = i["b"]
    c = i["c"]
    total = 0
    for i in range(100):
      x = i * 0.01
      total += (a*x*x+b*x+c-math.exp(x))**2
    return -total # higher scores == more fit individual

def demo_main():
    """Evolve an individual to maximize demo_score."""
    randomizer = random.Random()
    randomizer.seed(0)
    genome = { 
        "a": tuple(frange(-3,3,0.0001)), 
        "b": tuple(frange(-3,3,0.0001)), 
        "c": tuple(frange(-3,3,0.0001))}

    population = Population(genome,demo_score,randomizer)
    #population.addIndividual({"a":0.8389, "b":0.8515, "c":1.0129})
    population.addRandomIndividuals(100)
    generation=0
    population.sort()
    for generation in range(200):
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

def demo_seq_score(i):
  x = i["TestSequence"]
  return -((x-0.5)**2)

def demo_sequence():
  import stats
  genome = {"TestSequence" : Seq(lambda i : i**2, lambda x : x**0.5, 0, 1, 200000)}
  S = stats.Stats([roll(genome)["TestSequence"] for i in range(10000)],True)  # @UnusedVariable
  S.print() # mean should be near 1/3
  
  randomizer = random.Random()
  randomizer.seed(0)
  population = Population(genome,demo_seq_score,randomizer)
  population.addRandomIndividuals(100)
  population.sort()
  for generation in range(100):  # @UnusedVariable
    print(generation)
    population.evolve(mutation=0.20, elitism=2)
    population.sort()
    
  print("Top individuals:")
  for i in range(1,11):
    print("#%d %s" % (i, population.population[-i]))
    


if __name__=='__main__':
#     demo_sequence()
    demo_main()

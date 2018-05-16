import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pylab as plt
import requests

from .utils import force_str

base_url = 'http://websvc1.connectomes.utah.edu/{0}/OData/'


def validate_source(source):
    """
    Matches abbreviations to full volume names
    :param source: volume name or abbreviation
    :return:
    """
    if source == 'i':
        source = 'NeitzInferiorMonkey'
    elif source == 't':
        source = 'NeitzTemporalMonkey'
    elif source == 'r':
        source = 'RC1'
    return source


def get_volume_scale(source):
    """
    Matches source to volume scale, skips querying
    :param source: volume name or abbreviation
    :return: x,y,z dimensions in um/pixel, um/pixel, um/section
    """
    scale = np.array([1, 1, 1])
    source = validate_source(source)
    if source == 'RC1':
        scale = np.array([5, 5, 30,]) / 1000
    elif source == 'NeitzInferiorMonkey':
        scale = np.array([7.5, 7.5, 90,]) / 1000
    elif source == 'NeitzTemporalMonkey':
        scale = np.array([7.5, 7.5, 70,]) / 1000
    return scale


def get_structure_url(ID, source):
    """
    Returns basic OData query for a single Structure in Viking

    :param structure_id: Viking Structure ID
    :param source: volume name or abbreviation
    """
    source = validate_source(source)
    url = base_url.format(source) + 'Structures({0})/'.format(ID)
    return url


def get_location_url(structure_id, source):
    """
    Returns OData query for locations associated with a structure

    :param structure_id: Viking Structure ID
    :param source: volume name or abbreviation
    """
    url = get_structure_url(ID, source)
    url += 'Locations/'
    return url


def get_link_url(ID, source):
    """
    Returns OData query for locations associated with a structure

    :param structure_id: Viking Structure ID
    :param source: volume name or abbreviation
    """
    url = get_structure_url(ID, source)
    url += 'LocationLinks/?$select=A,B'
    return url


class Neuron(object):
    def __init__(self, structure_id, source):
        """
        Initializes Neuron object

        :param structure_id: Structure ID number
        :param source: volume name or abbreviation
        """
        self.structure_id = structure_id
        self.source = validate_source(source)
        self.scale = get_volume_scale(self.source)
        self.service_root = base_url.format(self.source)
        self.query = self.service_root + 'Structures({0})/'.format(
            self.structure_id)

        # Import location data
        r1 = requests.get(self.query + 'Locations/')
        j1 = r1.json()
        self.locations = pd.DataFrame(j1['value'])
        self.locations['Rum'] = self.locations['Radius'] * self.scale[1]

        self.soma_radius = self.locations['Rum'].max()

        # Import link data
        r2 = requests.get(get_link_url(self.structure_id, self.source))
        j2 = r2.json()
        self.links = pd.DataFrame(j2['value'])

    def __eq__(self, other):
        return self.structure_id == other.structure_id

    def __str__(self):
        # print('Neuron - c{0} in {1}'.format(self.ID, self.source))
        return force_str(u'<Neuron ID %s>' % self.structure_id)

    def graph(self, plot=False):
        """
        Returns a directed graph where the nodes represent annotations
        and the edges are the links between annotations.

        :param plot: whether or not to plot the graph (default = False)
        :return: nx.DiGraph
        """
        linkmat = np.array(self.links)
        g = nx.from_edgelist(linkmat)

        if plot:
            plt.subplot(111)
            nx.draw(g)

        return g

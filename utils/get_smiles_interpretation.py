import numpy as np
import networkx as nx
from rdkit import Chem
from karateclub import Graph2Vec


def smiles_to_graph(smiles: str) -> nx.Graph:
    mol = Chem.MolFromSmiles(smiles)

    print('Reading smile: %s' % smiles)

    graph = nx.Graph()

    for atom in mol.GetAtoms():
        graph.add_node(atom.GetIdx(),
                       atomic_num=atom.GetAtomicNum(),
                       is_aromatic=atom.GetIsAromatic(),
                       atom_symbol=atom.GetSymbol())

    for bond in mol.GetBonds():
        graph.add_edge(bond.GetBeginAtomIdx(),
                       bond.GetEndAtomIdx(),
                       bond_type=bond.GetBondType())

    return graph


def get_graph_vector(graph: nx.Graph) -> np.ndarray:
    model = Graph2Vec()

    model.fit([graph])
    graph_vec = model.get_embedding()

    return np.array(graph_vec)

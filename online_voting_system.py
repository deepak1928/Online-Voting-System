import datetime
import hashlib
import json
from flask import Flask,jsonify,request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Blockchain development
class online_voting_system:
    def __init__(self):
        self.chain=[]
        self.voters_details=[]
        self.votingID=[]
        self.create_block(proof =1,prev_hash='0')
        self.nodes=set()
   
    def create_block(self,proof,prev_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'voters_details':self.voters_details,
               'votingID':self.votingID,
               'prev_hash':prev_hash}
        self.voters_details=[]
        self.votingID=[]
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self):
        self.proof=True
        return self.proof
    
    def hash(self,block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        prev_block=chain[0]
        block_index=1
        while block_index < len(chain):
            block=chain[block_index]
            if block['prev_hash']!=self.hash(prev_block):
                return False
            if block['proof'] is False:
                return False
            prev_block=block
            block_index +=1
        return True
    
    def add_vote(self,voters_details,votingID):
        self.voters_details.append({'voters_details':voters_details})
        self.votingID.append({'votingID':votingID})
        prev_block=self.get_previous_block()
        return prev_block['index']+1
    
    def add_nodes(self,address):
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)

     
    def replace_chain(self):
        network =self.nodes
        longest_chain = []
        max_length=len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                chain = response.json()['chain']
                length = response.json()['length']
                
                if length > max_length() and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain =chain
        if longest_chain:
            self.chain= longest_chain
            return True
        return False
    
app=Flask(__name__)
node_address = str(uuid4()).replace('-','')
blockchain=online_voting_system()

@app.route('/mine_block',methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work()
    prev_hash = blockchain.hash(previous_block)
    blockchain.add_vote(voters_details=node_address,votingID='0')
    block = blockchain.create_block(proof,prev_hash)
    response = {'message' : 'Congratulation ,you have just mines an block',
                'index':block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'prev_hash': block['prev_hash'],
                'voters_details': block['voters_details'],
                'votingID':block['votingID']}
    return jsonify(response) ,200


 

@app.route('/get_chain',methods=['GET'])
def get_chain():
    response ={'chain': blockchain.chain,
               'length' :len(blockchain.chain)}
    
    return jsonify(response) ,200


@app.route('/is_valid',methods=['GET'])
def is_valid():
    valid_chain = blockchain.is_chain_valid(blockchain.chain)
    if valid_chain:
        response = {'message': 'blockchain is not valid '}
    else: 
        response={'message':'blockchain is valid .'}
    return jsonify(response), 200


@app.route('/add_vote',methods =['POST'])
def add_vote():
    json = request.get_json()
   # voting_keys ={'Name' , 'DOB','address','Id_number'}
    details={'Name':json['Name'],
             'DOB':json['DOB'],
             'address':json['address'],
             'ID_number':json['ID_number']}
    voting_details_hash=blockchain.hash(details)
   
    vote_detail={'hash_voting_details':voting_details_hash,
                 'vote':json['vote']}
    votingID_hash=blockchain.hash(vote_detail)
    index = blockchain.add_vote(voting_details_hash,votingID_hash )
    response = {'message' : f'this transaction is added in to Block{index}'}
    return jsonify(response) ,201

@app.route('/connect_node',methods =['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    response={'message':'all nodes are connected.Our Blockchain contains these node ',
              'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain',methods=['GET'])
def replace_chain():
    is_chain_replaced= blockchain.replace_chain()
    if is_chain_replaced:
        response ={'message':'the nodes had different chain .so chain is replaced And new chain is :',
                   'New_chain':blockchain.chain}
    else:
        response={'message':'All good all nodes have same chain',
                  'chain':blockchain.chain}
    return jsonify(response) ,200

app.run(host = '0.0.0.0',port = 5001)   
 
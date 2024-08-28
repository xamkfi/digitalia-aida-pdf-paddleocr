'''
Created on Nov 28, 2023

@author: memorylab-aj
'''
import torch

class cpugpupicker(object):
    '''
    classdocs
    '''


    def __init__(self):
        print("Initializing  {} module".format(type(self)))
        
        
    def getCPUorGPU(self):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        #print('Using device:', device)        
        #Additional Info when using cuda
        if device.type == 'cuda':            
            print('Allocated memory: {}'.format( round(torch.cuda.memory_allocated(0)/1024**3,1), 'GB'))
            print('Cached memory:  {} '.format( round(torch.cuda.memory_reserved(0)/1024**3,1), 'GB'))
            print("Cuda version: {}".format(torch.version.cuda))
            print("Cuda available: {}".format(torch.cuda.is_available()))
            print("Cuda devices: {}".format(torch.cuda.device_count()))
            for i in range(torch.cuda.device_count()):
                print("Device {} = {}".format(i, torch.cuda.get_device_properties(i).name))        
        return device
    
    
    
    
    
    
    
    
    
    
    
    
    
# ! classification 
# using knowledge from hands on machine learning
'''

How image classification works (simplified):

A pretrained CNN (like ResNet) was trained on millions of labeled images (ImageNet — 1000 categories). It learned to extract visual features: edges → textures → shapes → objects, layer by layer. When you feed it a new image, it outputs probability scores for each category. You take the top few as your tags.

Transfer learning means you use that pretrained model as-is (or fine-tune it on your own data). You skip the expensive training step entirely — just load the weights, preprocess the image, and run inference.

'''
'''

plan / my process:
1) user will upload image
2) resized to proper image format
3) run it through pretrained model
4) get back probability scores
5) return top 5 labels

'''


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

to-do
add dependencies
implement classify(image) which returns a (label, confidence)
    step a
    call the model with weights (torchvision.models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2))
    call .eval()

    step b
    preprocessing
    weights = ResNet50_Weights.IMAGENET1K_V2
    preprocess = weights.transforms()

    step c - run the model
    with torch.no_grad():
        output = model(batch) 
    probabilities = torch.nn.functional.softmax(output[0], dim=0) # turning raw scores into probabilities
    top5_prob, top5_idx = torch.topk(probabilities, 5) # find 5 top probabilities

    step d - turn the indexes into weights
    categories = weights.meta["categories"]
    [{"label": categories[idx], "confidence": prob.item()} 
        for idx, prob in zip(top5_idx, top5_prob)] # create a list of index, and confidence
    
add POST /ml/classify
add frontend button
add test
update apers

'''


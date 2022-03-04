python week3/createContentTrainingData.py  --build False --min_products 25

shuf -o /workspace/datasets/categories/output_filtered.fasttext < /workspace/datasets/categories/output_filtered.fasttext 
head -n 10000 /workspace/datasets/categories/output_filtered.fasttext > /workspace/datasets/categories/categories.train 
tail -10000 /workspace/datasets/categories/output_filtered.fasttext > /workspace/datasets/categories/categories.test 

~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/categories/categories.train -output /workspace/datasets/categories/model_categories -lr 1.0 -epoch 25
~/fastText-0.9.2/fasttext test /workspace/datasets/categories/model_categories.bin /workspace/datasets/categories/categories.test 
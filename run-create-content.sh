python week3/createContentTrainingData.py --min_products 200 --build True

shuf -o /workspace/datasets/product_data/categories/output_filtered.fasttext < /workspace/datasets/product_data/categories/output_filtered.fasttext 
head -n 10000 /workspace/datasets/product_data/categories/output_filtered.fasttext > /workspace/datasets/product_data/categories/categories.train 
tail -10000 /workspace/datasets/product_data/categories/output_filtered.fasttext > /workspace/datasets/product_data/categories/categories.test 

~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/product_data/categories/categories.train -output /workspace/datasets/product_data/categories/model_categories -lr 1.0 -epoch 50 -wordNgrams 2 -maxn 0
~/fastText-0.9.2/fasttext test /workspace/datasets/product_data/categories/model_categories.bin /workspace/datasets/product_data/categories/categories.test 
You could leverage pre-trained models like VGGish, OpenL3, or wav2vec 2.0, which are trained on large-scale audio datasets for embedding extraction,Once you have obtained audio embeddings for both the original song's vocals and the user's vocals, you can leverage these embeddings to calculate a similarity score for your project. Here's a general approach you could follow:

1. **Obtain Embeddings**:
   - Use a pre-trained model (e.g., OpenL3, VGGish, wav2vec 2.0) or train your own model to extract embeddings from the original song's vocals and the user's vocals.
   - Let's assume you have two embedding vectors: `original_embedding` and `user_embedding`.

2. **Calculate Similarity**:
   - There are several ways to measure the similarity between two embedding vectors. A common approach is to calculate the cosine similarity, which measures the cosine of the angle between the two vectors.
   - Cosine similarity ranges from -1 to 1, where 1 indicates that the vectors are identical, and -1 indicates that they are completely opposite.
   - To calculate the cosine similarity, you can use the following formula:

     ```python
     import numpy as np

     def cosine_similarity(a, b):
         return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

     similarity_score = cosine_similarity(original_embedding, user_embedding)
     ```

3. **Interpret the Similarity Score**:
   - The similarity score ranges from -1 to 1, where a higher score indicates greater similarity between the user's vocals and the original song's vocals.
   - You can interpret the score based on your specific requirements. For example, you could consider a score above 0.8 as "highly similar," a score between 0.5 and 0.8 as "similar," and a score below 0.5 as "dissimilar."

4. **Additional Processing (Optional)**:
   - Depending on your project's requirements, you might want to perform additional processing on the embeddings or the similarity score.
   - For example, you could weight different dimensions of the embedding vectors based on their importance for your specific task (e.g., giving more weight to pitch-related dimensions).
   - Alternatively, you could combine the cosine similarity score with other features or metrics (e.g., pitch accuracy, timing accuracy) to create a more comprehensive scoring system.

5. **Evaluation and Fine-tuning**:
   - Evaluate the performance of your similarity scoring system on a held-out test set or through user feedback.
   - If necessary, you can fine-tune the pre-trained model or train your own model specifically for your task, using a metric learning objective or a contrastive loss function to learn embeddings that better capture the relevant similarities for your project.

By following this approach, you can leverage audio embeddings to calculate a similarity score between the user's vocals and the original song's vocals. This score can then be used as part of your overall scoring system or integrated with other components of your project.

Note that the effectiveness of this approach will depend on the quality and relevance of the audio embeddings, as well as the specific characteristics of your dataset and task. It's often beneficial to experiment with different embedding models, similarity metrics, and additional processing techniques to find the best solution for your particular use case.
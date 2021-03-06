# examples/text_classification/rnn/model.py

import paddle
import paddle.nn as nn
import paddlenlp as nlp
import numpy as np


class FastText(nn.Layer):
    """
    This class implements the fastText model to classify texts.
    At a high level, the model starts by embedding the tokens and running them through
    a word embedding. Then, we encode these representations with a `BoWEncoder`.
    Lastly, we take the output of the encoder to create a final representation,
    which is passed through one final feed-forward layer to output a logits (`output_layer`).
    """

    def __init__(self, vocab_size, num_classes, emb_dim):
        super().__init__()

        self.embedder = nn.Embedding(vocab_size, emb_dim)
        weight = (np.random.rand(vocab_size, emb_dim) * 2 - 1) / emb_dim
        self.embedder.weight.set_value(weight.astype('float32'))

        self.bow_encoder = nlp.seq2vec.BoWEncoder(emb_dim)

        weight_attr = paddle.ParamAttr(
            name="weight", initializer=paddle.nn.initializer.Constant(value=0))
        self.output_layer = nn.Linear(
            emb_dim, num_classes, weight_attr=weight_attr, bias_attr=False)

    def forward(self, text, seq_len=None):
        # Shape: (batch_size, seq_len, embedding_dim)
        embedded_text = self.embedder(text)
        # Shape: (batch_size, embedding_dim)
        summed = self.bow_encoder(embedded_text)
        summed = summed / embedded_text.shape[1]
        # Shape: (batch_size, num_classes)
        logits = self.output_layer(summed)
        return logits

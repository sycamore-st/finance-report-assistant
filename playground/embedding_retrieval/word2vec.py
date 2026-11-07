from __future__ import annotations

import io
import re
import string

import numpy as np
import tensorflow as tf
import tqdm
from tensorflow.keras import layers

SEED = 42
AUTOTUNE = tf.data.AUTOTUNE


def generate_training_data(
    sequences: list[np.ndarray],
    window_size: int,
    num_ns: int,
    vocab_size: int,
    seed: int,
) -> tuple[list[int], list[tf.Tensor], list[tf.Tensor]]:
    targets: list[int] = []
    contexts: list[tf.Tensor] = []
    labels: list[tf.Tensor] = []

    sampling_table = tf.keras.preprocessing.sequence.make_sampling_table(vocab_size)

    for sequence in tqdm.tqdm(sequences):
        positive_skip_grams, _ = tf.keras.preprocessing.sequence.skipgrams(
            sequence,
            vocabulary_size=vocab_size,
            sampling_table=sampling_table,
            window_size=window_size,
            negative_samples=0,
            seed=seed,
        )

        for target_word, context_word in positive_skip_grams:
            context_class = tf.expand_dims(tf.constant([context_word], dtype="int64"), 1)
            negative_sampling_candidates, _, _ = tf.random.log_uniform_candidate_sampler(
                true_classes=context_class,
                num_true=1,
                num_sampled=num_ns,
                unique=True,
                range_max=vocab_size,
                seed=seed,
                name="negative_sampling",
            )

            context = tf.concat([tf.squeeze(context_class, 1), negative_sampling_candidates], 0)
            label = tf.constant([1] + [0] * num_ns, dtype="int64")

            targets.append(target_word)
            contexts.append(context)
            labels.append(label)

    return targets, contexts, labels


def custom_standardization(input_data: tf.Tensor) -> tf.Tensor:
    lowercase = tf.strings.lower(input_data)
    return tf.strings.regex_replace(lowercase, "[%s]" % re.escape(string.punctuation), "")


class Word2Vec(tf.keras.Model):
    def __init__(self, vocab_size: int, embedding_dim: int):
        super().__init__()
        self.target_embedding = layers.Embedding(vocab_size, embedding_dim, name="w2v_embedding")
        self.context_embedding = layers.Embedding(vocab_size, embedding_dim)

    def call(self, pair: tuple[tf.Tensor, tf.Tensor]) -> tf.Tensor:
        target, context = pair
        if len(target.shape) == 2:
            target = tf.squeeze(target, axis=1)

        word_emb = self.target_embedding(target)
        context_emb = self.context_embedding(context)
        dots = tf.einsum("be,bce->bc", word_emb, context_emb)
        return dots


def build_dataset(vocab_size: int = 4096, sequence_length: int = 10) -> tuple[tf.data.Dataset, layers.TextVectorization]:
    path_to_file = tf.keras.utils.get_file(
        "shakespeare.txt",
        "https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt",
    )

    text_ds = tf.data.TextLineDataset(path_to_file).filter(
        lambda x: tf.cast(tf.strings.length(x), bool)
    )

    vectorize_layer = layers.TextVectorization(
        standardize=custom_standardization,
        max_tokens=vocab_size,
        output_mode="int",
        output_sequence_length=sequence_length,
    )
    vectorize_layer.adapt(text_ds.batch(1024))

    text_vector_ds = text_ds.batch(1024).prefetch(AUTOTUNE).map(vectorize_layer).unbatch()
    sequences = list(text_vector_ds.as_numpy_iterator())

    targets, contexts, labels = generate_training_data(
        sequences=sequences,
        window_size=2,
        num_ns=4,
        vocab_size=vocab_size,
        seed=SEED,
    )

    targets_np = np.array(targets)
    contexts_np = np.array(contexts)
    labels_np = np.array(labels)

    batch_size = 1024
    buffer_size = 10000
    dataset = tf.data.Dataset.from_tensor_slices(((targets_np, contexts_np), labels_np))
    dataset = dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)
    dataset = dataset.cache().prefetch(buffer_size=AUTOTUNE)

    return dataset, vectorize_layer


def train_word2vec(
    dataset: tf.data.Dataset,
    vocab_size: int = 4096,
    embedding_dim: int = 128,
    epochs: int = 20,
) -> Word2Vec:
    model = Word2Vec(vocab_size, embedding_dim)
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="logs")
    model.fit(dataset, epochs=epochs, callbacks=[tensorboard_callback])
    return model


def export_embeddings(model: Word2Vec, vectorize_layer: layers.TextVectorization) -> None:
    weights = model.get_layer("w2v_embedding").get_weights()[0]
    vocab = vectorize_layer.get_vocabulary()

    with io.open("vectors.tsv", "w", encoding="utf-8") as out_v, io.open(
        "metadata.tsv", "w", encoding="utf-8"
    ) as out_m:
        for index, word in enumerate(vocab):
            if index == 0:
                continue
            vec = weights[index]
            out_v.write("\t".join(str(x) for x in vec) + "\n")
            out_m.write(word + "\n")


def main() -> None:
    vocab_size = 4096
    dataset, vectorize_layer = build_dataset(vocab_size=vocab_size, sequence_length=10)
    model = train_word2vec(dataset, vocab_size=vocab_size, embedding_dim=128, epochs=20)
    export_embeddings(model, vectorize_layer)


if __name__ == "__main__":
    main()

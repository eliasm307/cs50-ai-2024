import sys
from typing import Any, Tuple, Union
import tensorflow as tf

from PIL import Image, ImageDraw, ImageFont
from transformers import (
    AutoTokenizer,
    TFBertForMaskedLM,
    BatchEncoding,
)
from transformers.modeling_tf_outputs import TFMaskedLMOutput

# Pre-trained masked language model
MODEL = "bert-base-uncased"

# Number of predictions to generate
K = 3

# Constants for generating attention diagrams
FONT = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 28)
GRID_SIZE = 40
PIXELS_PER_WORD = 200

AttentionWeightsMatrix = list[list[float]]

# This is to approximate the shape of a tensor's data and how to access it
TensorData = list[list[AttentionWeightsMatrix]]


def main():
    text = input("Text: ")

    # Tokenize input
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    inputs = tokenizer(text, return_tensors="tf")
    mask_token_index = get_mask_token_index(tokenizer.mask_token_id, inputs)
    if mask_token_index is None:
        sys.exit(f"Input must include mask token {tokenizer.mask_token}.")

    # Use model to process input
    model: Any = TFBertForMaskedLM.from_pretrained(MODEL)
    result: TFMaskedLMOutput = model(**inputs, output_attentions=True)

    # Generate predictions
    mask_token_logits = result.logits[0, mask_token_index]  # type: ignore
    top_tokens = tf.math.top_k(mask_token_logits, K).indices.numpy()
    for token in top_tokens:
        print(text.replace(tokenizer.mask_token, tokenizer.decode([token])))

    # Visualize attentions
    visualize_attentions(inputs.tokens(), result.attentions)  # type: ignore


def get_mask_token_index(mask_token_id: int | None, inputs: BatchEncoding):
    """
    Return the index of the token with the specified `mask_token_id`, or
    `None` if not present in the `inputs`.
    """
    if mask_token_id is None:
        return

    # typing is a mess here but inputs["input_ids"] is an EagerTensor which currently doesn't have typing for the methods it exposes, e.g. "numpy"
    input_ids: list[int] = inputs["input_ids"][0].numpy().tolist()  # type: ignore
    if mask_token_id in input_ids:
        return input_ids.index(mask_token_id)


def get_color_for_attention_score(attention_score: float):
    """
    Return a tuple of three integers representing a shade of gray for the
    given `attention_score`. Each value should be in the range [0, 255].
    """
    colour_weight = int(attention_score * 255)
    return (colour_weight, colour_weight, colour_weight)


def visualize_attentions(tokens: list[str], attentions: list[TensorData]):
    """
    Produce a graphical representation of self-attention scores.

    For each attention layer, one diagram should be generated for each
    attention head in the layer. Each diagram should include the list of
    `tokens` in the sentence. The filename for each diagram should
    include both the layer number (starting count from 1) and head number
    (starting count from 1).
    """
    layers_count = len(attentions)
    heads_count = len(attentions[0][0])

    # produce diagrams for all layers and heads.
    beam_index = 0  # fixed
    for layer_index in range(layers_count):
        for head_index in range(heads_count):
            generate_diagram(
                layer_number=layer_index + 1,
                head_number=head_index + 1,
                tokens=tokens,
                attention_weights=attentions[layer_index][beam_index][head_index],
            )


def generate_diagram(
    layer_number: int,
    head_number: int,
    tokens: list[str],
    attention_weights: AttentionWeightsMatrix,
):
    """
    Generate a diagram representing the self-attention scores for a single
    attention head. The diagram shows one row and column for each of the
    `tokens`, and cells are shaded based on `attention_weights`, with lighter
    cells corresponding to higher attention scores.

    The diagram is saved with a filename that includes both the `layer_number`
    and `head_number`.
    """
    # Create new image
    image_size = GRID_SIZE * len(tokens) + PIXELS_PER_WORD
    img = Image.new("RGBA", (image_size, image_size), "black")
    draw = ImageDraw.Draw(img)

    # Draw each token onto the image
    for i, token in enumerate(tokens):
        # Draw token columns
        token_image = Image.new("RGBA", (image_size, image_size), (0, 0, 0, 0))
        token_draw = ImageDraw.Draw(token_image)
        token_draw.text(
            (image_size - PIXELS_PER_WORD, PIXELS_PER_WORD + i * GRID_SIZE),
            token,
            fill="white",
            font=FONT,
        )
        token_image = token_image.rotate(90)
        img.paste(token_image, mask=token_image)

        # Draw token rows
        _, _, width, _ = draw.textbbox((0, 0), token, font=FONT)
        draw.text(
            (PIXELS_PER_WORD - width, PIXELS_PER_WORD + i * GRID_SIZE),
            token,
            fill="white",
            font=FONT,
        )

    # Draw each word
    for i in range(len(tokens)):
        y = PIXELS_PER_WORD + i * GRID_SIZE
        for j in range(len(tokens)):
            x = PIXELS_PER_WORD + j * GRID_SIZE
            color = get_color_for_attention_score(attention_weights[i][j])
            draw.rectangle((x, y, x + GRID_SIZE, y + GRID_SIZE), fill=color)

    # Save image
    img.save(f"Attention_Layer{layer_number}_Head{head_number}.png")


if __name__ == "__main__":
    main()

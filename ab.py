def organize_pyramid(file_name):
    with open(file_name, 'r') as file:
        lines = [line.strip().split() for line in file]

    pyramid = []
    current_row = []
    for line in lines:
        number = int(line[0])
        word = line[1]
        current_row.append(word)

        if len(current_row) == number:
            pyramid.append(current_row)
            current_row = []

    return pyramid


def decode_secret(file_name):
    pyramid = organize_pyramid(file_name)

    decoded_numbers = [len(row) for row in pyramid]

    decoded_message = ' '.join(pyramid[i][-1] for i in range(len(pyramid)))
    return decoded_message


result = decode_secret("coding_challenge_input.txt")
print(result)

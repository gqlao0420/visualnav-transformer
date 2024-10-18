import argparse
import os
import shutil
import random

# 这段Python代码定义了一个函数 remove_files_in_dir，它接受一个目录路径 dir_path 作为参数，并删除该目录下的所有文件和子目录。
# 使用此函数时要小心，因为它会永久删除文件和目录。在运行此函数之前，请确保你不想保留目录中的任何文件或目录
def remove_files_in_dir(dir_path: str):
    # 这行代码列出 dir_path 指定的目录下的所有文件和子目录，并迭代每一个项
    for f in os.listdir(dir_path):
        # 对于每个项，使用 os.path.join 构建完整的文件路径
        file_path = os.path.join(dir_path, f)
        # try...except 块：尝试执行删除操作，如果遇到任何异常，则捕获异常并打印错误信息
        try:
            # 检查 file_path 是否是一个文件或符号链接
            if os.path.isfile(file_path) or os.path.islink(file_path):
                # 如果 file_path 是文件或符号链接，使用 os.unlink 删除它
                os.unlink(file_path)
            # 如果 file_path 是一个目录，执行下面的 shutil.rmtree(file_path)
            elif os.path.isdir(file_path):
                # 如果 file_path 是目录，使用 shutil.rmtree 删除该目录及其所有内容
                shutil.rmtree(file_path)
        # 如果删除操作失败，打印出未能删除的文件路径和失败原因
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def main(args: argparse.Namespace):
    # Get the names of the folders in the data directory that contain the file 'traj_data.pkl'
    # 列表推导式，用于从指定的目录 args.data_dir 中筛选出满足特定条件的子目录名称.
    folder_names = [
        f
        # 列出 args.data_dir 目录下的所有文件和子目录名称。
        for f in os.listdir(args.data_dir)
        # 对于每个项 f，检查它是否是一个目录。这是通过将 args.data_dir 和 f 结合成完整的路径，并使用 os.path.isdir() 函数来完成的。
        if os.path.isdir(os.path.join(args.data_dir, f))
        # 如果 f 是一个目录，进一步检查该目录中是否包含名为 "traj_data.pkl" 的文件。这同样是通过结合 args.data_dir 和 f 形成完整路径，并列出该目录下的所有文件来完成的。
        and "traj_data.pkl" in os.listdir(os.path.join(args.data_dir, f))
    ]
    # folder_names = [...]： 将所有满足上述条件的目录名称收集到一个列表 folder_names 中。


    # Randomly shuffle the names of the folders
    # random.shuffle 函数用于将一个列表中的元素随机打乱顺序。这个函数直接修改原始列表，而不返回新的列表。
    random.shuffle(folder_names)

    # Split the names of the folders into train and test sets
    # 这段代码的目的是将 folder_names 列表分割成两个部分：train_folder_names 和 test_folder_names。
    # 这通常用于机器学习中的数据集分割，其中一部分数据用于训练模型，另一部分用于测试模型。
    # args.split 应该是一个介于 0 和 1 之间的小数，表示训练集占总数据集的比例。例如，如果 args.split 是 0.8，那么 80% 的数据将被用于训练，剩下的 20% 将被用于测试。
    split_index = int(args.split * len(folder_names))
    # 将 folder_names 列表从开始到 split_index（不包括 split_index）的部分分配给 train_folder_names。这意味着 train_folder_names 包含了用于训练的文件夹名称。
    train_folder_names = folder_names[:split_index]
    # 将 folder_names 列表从 split_index 到末尾的部分分配给 test_folder_names。
    test_folder_names = folder_names[split_index:]

    # Create directories for the train and test sets
    train_dir = os.path.join(args.data_splits_dir, args.dataset_name, "train")
    test_dir = os.path.join(args.data_splits_dir, args.dataset_name, "test")
    for dir_path in [train_dir, test_dir]:
        if os.path.exists(dir_path):
            print(f"Clearing files from {dir_path} for new data split")
            remove_files_in_dir(dir_path)
        else:
            print(f"Creating {dir_path}")
            os.makedirs(dir_path)

    # Write the names of the train and test folders to files
    with open(os.path.join(train_dir, "traj_names.txt"), "w") as f:
        for folder_name in train_folder_names:
            f.write(folder_name + "\n")

    with open(os.path.join(test_dir, "traj_names.txt"), "w") as f:
        for folder_name in test_folder_names:
            f.write(folder_name + "\n")


if __name__ == "__main__":
    # Set up the command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data-dir", "-i", help="Directory containing the data", required=True
    )
    parser.add_argument(
        "--dataset-name", "-d", help="Name of the dataset", required=True
    )
    parser.add_argument(
        "--split", "-s", type=float, default=0.8, help="Train/test split (default: 0.8)"
    )
    parser.add_argument(
        "--data-splits-dir", "-o", default="vint_train/data/data_splits", help="Data splits directory"
    )
    args = parser.parse_args()
    main(args)
    print("Done")

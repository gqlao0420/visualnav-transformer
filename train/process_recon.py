import h5py
import os
import pickle
from PIL import Image
import io
import argparse
import tqdm


def main(args: argparse.Namespace):
    # 这行代码的作用是将 args.input_dir 和 "recon_release" 连接起来，形成一个完整的目录路径，并将其存储在变量 recon_dir 中
    recon_dir = os.path.join(args.input_dir, "recon_release")
    output_dir = args.output_dir

    # create output dir if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # get all the folders in the recon dataset
    # 列出 recon_dir 目录下的所有文件和目录
    # 如果 args.num_trajs 大于或等于0，只保留前 args.num_trajs 个文件名
    # 这里 args.num_trajs 可能是一个命令行参数，用于指定你想要处理的轨迹数量。例如，如果你只想处理前5个轨迹，你可以通过命令行参数 --num_trajs 5 来设置这个值。
    filenames = os.listdir(recon_dir)
    if args.num_trajs >= 0:
        filenames = filenames[: args.num_trajs]

    # processing loop
    # 使用了 tqdm 库来显示一个进度条，该进度条在处理 filenames 列表中的每个元素时更新。
    # tqdm 是一个快速，可扩展的Python进度条库，可以在长循环中添加一个进度条，以便用户可以实时看到进度。
    for filename in tqdm.tqdm(filenames, desc="Trajectories processed"):
        # extract the name without the extension
        # 对于每个文件名，通过分割文件名并去除扩展名来提取轨迹名称（traj_name）
        traj_name = filename.split(".")[0]
        # load the hdf5 file
        try:
            # 尝试打开位于 recon_dir 目录下的 HDF5 文件（使用 h5py.File），如果打开文件时发生 OSError 异常，则打印错误信息并跳过当前文件。
            h5_f = h5py.File(os.path.join(recon_dir, filename), "r")
        except OSError:
            print(f"Error loading {filename}. Skipping...")
            continue
        # extract the position and yaw data
        # 从 HDF5 文件中提取 position 和 yaw 数据，并将它们保存到字典 traj_data 中
        # 这行代码从 HDF5 文件中名为 h5_f 的组中读取 "jackal" 组内的 "position" 数据集。
        # 使用 [:, :2] 这个切片操作符，它提取了 "position" 数据集中的所有行（代表不同的时间点或轨迹点）和前两列（通常代表 x 和 y 坐标）。
        # 这样，position_data 变量就包含了机器人在二维空间中的轨迹位置数据。
        position_data = h5_f["jackal"]["position"][:, :2]
        # 这行代码从相同的 "jackal" 组中读取 "yaw" 数据集。使用 [()] 这个操作符，它提取了整个 "yaw" 数据集的值。
        # "yaw" 数据集通常包含机器人在每个时间点的方向数据，即机器人相对于某个参考方向（如正北）的旋转角度。
        # yaw_data 变量因此包含了机器人的朝向信息。
        yaw_data = h5_f["jackal"]["yaw"][()]
        # save the data to a dictionary
        traj_data = {"position": position_data, "yaw": yaw_data}
        traj_folder = os.path.join(output_dir, traj_name)
        # os.makedirs() 函数用于递归创建目录
        # traj_folder：这是你想要创建的目录路径
        # exist_ok=True：这个参数告诉 os.makedirs() 如果目录已经存在，则不要抛出异常。在默认情况下（即 exist_ok=False），
        # 如果目标目录已经存在，os.makedirs() 会抛出一个 FileExistsError 异常。
        # 设置 exist_ok=True 可以防止这种情况，使得即使目录已经存在，代码也不会出错，能够继续执行。
        os.makedirs(traj_folder, exist_ok=True)

        # os.path.join(traj_folder, "traj_data.pkl")：这个函数调用将traj_folder变量（它包含了一个目录路径）和字符串"traj_data.pkl"（这是要创建的文件的名称）
        # 连接起来，形成完整的文件路径。os.path.join函数可以确保路径在不同操作系统上正确无误，因为它会根据操作系统使用正确的路径分隔符。
        # with open(..., "wb") as f：这是一个上下文管理器，它以二进制写入模式（"wb"）打开文件。with语句是Python中的一个语法糖，它可以确保文件在使用后正确关闭，
        # 即使在写入数据时发生异常也是如此。
        # pickle.dump(traj_data, f)：这个函数调用将traj_data字典序列化，并将序列化后的数据写入到之前打开的文件对象f中。
        # pickle模块可以序列化Python中的许多数据类型，包括字典、列表、集合、类实例等。
        # 总的来说，这段代码的作用是将traj_data字典保存到traj_folder目录下名为traj_data.pkl的文件中。这种序列化方法不仅保存了数据的内容，还保存了数据类型，
        # 因此在之后读取文件并反序列化时，可以恢复原始的Python数据结构。
        with open(os.path.join(traj_folder, "traj_data.pkl"), "wb") as f:
            pickle.dump(traj_data, f)
        # make a folder for the file
        if not os.path.exists(traj_folder):
            os.makedirs(traj_folder)
        # save the image data to disk
        for i in range(h5_f["images"]["rgb_left"].shape[0]):
            img = Image.open(io.BytesIO(h5_f["images"]["rgb_left"][i]))
            img.save(os.path.join(traj_folder, f"{i}.jpg"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # get arguments for the recon input dir and the output dir
    parser.add_argument(
        # 指定 recon_dataset 的输入目录路径。这是一个必需参数，类型为字符串。
        "--input-dir",
        "-i",
        type=str,
        help="path of the recon_dataset",
        required=True,
    )
    parser.add_argument(
        # 指定处理后的 recon_dataset 的输出目录路径。默认值为 datasets/recon/，类型为字符串。
        "--output-dir",
        "-o",
        default="datasets/recon/",
        type=str,
        help="path for processed recon dataset (default: datasets/recon/)",
    )
    # number of trajs to process
    parser.add_argument(
        # 指定要处理的轨迹数量。默认值为 -1，表示处理所有轨迹，类型为整数。
        "--num-trajs",
        "-n",
        default=-1,
        type=int,
        help="number of trajectories to process (default: -1, all)",
    )

    args = parser.parse_args()
    print("STARTING PROCESSING RECON DATASET")
    main(args)
    print("FINISHED PROCESSING RECON DATASET")

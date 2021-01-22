def main():
    load_rps = [1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 2.0, 1.0, 2.0]
    if max(load_rps[1:]) < load_rps[0]:
        print("ScaleUp")
        print(max(load_rps))
    elif max(load_rps[1:]) > load_rps[0] :        
        # load_rps.remove(max(load_rps))
        n=max(load_rps)
        while n==max(load_rps):
            load_rps.remove(max(load_rps))
        print(max(load_rps))
    elif all(i == load_rps[0] for i in load_rps):
            print("test")

if __name__ == "__main__":
    main()
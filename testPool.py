#coding: utf-8

from multiprocessing import Pool #线程池模块
import time,os,random

# def testPoolFunc(msg):
#     print("hello:%s",msg)
#     time.sleep(3)
#     print("end")
#
# if __name__ == "__main__":
#     pool = Pool(processes=2)    # 创建一个大小为2的线程池
#     for i in range(4):
#         msg = "num is %s"%i
#         # 维持线程池内的数据量为processes
#         # 非阻塞式线程池
#         #pool.apply_async(testPoolFunc,(msg,))
#         # 非阻塞式线程池
#         pool.apply(testPoolFunc,(msg,))
#     print("start ----+++++++++")
#     # 调用join之前，现调用close函数，否则会出错。(类似于清理pool)
#     # 执行完close后不会有新的线程加入到pool中。
#     # join函数等待所有子线程结束
#     pool.close()
#     pool.join()
#     print("over ------+++++++")



# def testFunc(msg):
#     print("msg->",msg)
#     time.sleep(2)
#     print("end")
#     # 返回线程中的数据
#     return "done"+msg
#
# if __name__ == "__main__":
#     pool = Pool(processes=4)
#     result = []
#     for i in range(3):
#         msg = "hello : %s"%i
#         # 添加数据进数组result
#         result.append(pool.apply_async(testFunc,(msg,)))
#     pool.close()
#     pool.join()
#     for item in result:
#         # 解析数组中元素的get值
#         print(":::",item.get())
#     print("end;")


def oneF():
    print("\nRun task Frank-",(os.getpid()))
    start = time.time()
    time.sleep(random.random() * 1)
    end = time.time()
    print('Task Frank runs %0.2f seconds.' % (end - start))
def twoF():
    print("\nRun task Frank-", (os.getpid()))
    start = time.time()
    time.sleep(random.random() * 2)
    end = time.time()
    print('Task Frank runs %0.2f seconds.' % (end - start))
def threeF():
    print("\nRun task Frank-", (os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task Frank runs %0.2f seconds.' % (end - start))
def fourF():
    print("\nRun task Frank-", (os.getpid()))
    start = time.time()
    time.sleep(random.random() * 4)
    end = time.time()
    print('Task Frank runs %0.2f seconds.' % (end - start))

if __name__ == "__main__":
    funcList = [oneF,twoF,threeF,fourF]
    print("parent prcess ",os.getpid())

    pool = Pool(4)
    for funcItem in funcList:
        pool.apply_async(funcItem)

    print("start")
    pool.close()
    pool.join()
    print("end")

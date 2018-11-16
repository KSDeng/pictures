



<h1 style="text-align:center">
    《高级程序设计》第五次作业实验报告
</h1>

<center><b></b><font size=4 >邓开圣161220031</font></b></center>

## 1.效果展示
<div align="center">
    <img src="https://github.com/KSDeng/pictures/blob/master/pictures/result1.gif?raw=true" width = 600 height = 400><br>添加、删除、清空<br><br>
    <img src="https://github.com/KSDeng/pictures/blob/master/pictures/result2.gif?raw=true" width = 600 height = 400><br>文件载入和保存<br><br>
	<img src="https://github.com/KSDeng/pictures/blob/master/pictures/result3.gif?raw=true" width = 600 height = 400><br>门禁系统基本功能<br><br>
</div>






## 2.设计思路
本项目的主要结构如下: 

<div align="center"> </div>

<div align = 'center'><img src="https://github.com/KSDeng/pictures/blob/master/pictures/classes.PNG?raw=true" height="300" width="250"></img>    
</div>




类按窗口和功能进行组织，项目共有5个类：   
1. 主窗口类  mainwindow  
2. 管理员类 administrator  
3. 添加准入信息类 addInfo  
4. 门禁系统类 access  
5. 添加出入信息类 AddAccessAction  

这5个类均对应三个文件(.h文件、.cpp文件和.ui文件)，其功能分别是类声明、类定义和类的界面。它们之间的关系如下:   

<div align="center">
    <img src="https://github.com/KSDeng/pictures/blob/master/pictures/classStructure.PNG?raw=true" width = 400 height = 300>
</div>



**这里的树结构不表示继承关系，而表示父结点对应的类的对象中拥有子节点所对应的类的对象作为对象成员。程序通过这种方式进行组织，从而实现“根节点的对象中发生某个事件时，将对象成员所对应的窗口调出”的效果，以进行进一步的操作。**   
另外，globaluse.h和globaluse.cpp文件中定义和实现了一些需要全局使用的数据结构/函数。关于这些类和数据结构，以下将进行更为详细的介绍。

## 3.主要数据结构
* PermitInfo
```c++
//globaluse.h
//表示一条准入信息的结构体
struct PermitInfo{
    QString name;  
    QString identity;    
    QString cardID;  
    QString faceID;  
    ...
};

```

* MoveInfo
```c++
//globaluse.h
//表示一条出入信息的结构体
struct MoveInfo{
    QString identity;
    QString cardID;
    QString faceID;
    QString direction;
    //QTime actionTime;   //进/出的时间
    QString actionTime;
    ...
};
```

* permitInfoVector、moveInfoVector
```c++
//globaluse.cpp
vector <PermitInfo> permitInfoVector;  //存储准入信息的vector
vector <MoveInfo>   moveInfoVector;    //存储出入信息的vector
```
## 4.类介绍
### mainwindow

功能:提供初始主界面和打开管理员界面/门禁系统界面的入口。
```c++
//mainwindow.h
...
private slots:
    void on_Btn_InfoAdmin_clicked();	//打开管理员界面的槽函数

    void on_Btn_AccessSystem_clicked();	//打开门禁系统界面的槽函数

private:
    Ui::MainWindow *ui;
    Administrator admin;            //管理员后台
    Access accessSystem;            //门禁系统
```
### Administrator
功能:提供管理员界面和管理准入信息的相关功能，包括添加、删除、清空、保存(写文件)、载入(读文件)等，相应的处理事件通过点击界面上的按钮触发。
```c++
//administrator.h
...
private slots:
    void on_Btn_AddInfo_clicked();

    void on_Btn_ClearInfo_clicked();

    void on_Btn_DeleteInfo_clicked();

    void on_Btn_SaveInfo_clicked();

    void on_Btn_LoadInfo_clicked();

private:
    Ui::Administrator *ui;
    AddInfo addInfo;            //添加信息界面
```
### Access
功能:提供门禁系统界面和处理出入信息的相关功能,包括添加、删除、清空、提交(根据当前准入信息判断出入行为是否合法)等，相应的功能均通过点击界面上的按钮触发。
```c++
//access.h
...
private slots:

    void on_Btn_addAccessInfo_clicked();

    void on_Btn_deleteAccessInfo_clicked();

    void on_Btn_clearAccessInfo_clicked();

    void on_Btn_submitAccessInfo_clicked();

private:
    Ui::Access *ui;
    AddAccessAction addaccessaction;    //添加出入动作
```
### addInfo
功能:实现添加准入信息的功能，在输入的同时进行信息的合法性判断，例如：
```c++
//addInfo.cpp
    ...
    //添加过程中进行合法性检查
    if(addName.length()==0 || addCardID.length()==0){
        QMessageBox::warning(this,"警告","信息不完整,请重新检查","确定");
        return;
    }

    //qDebug()<<addName<<" "<<addIdentity<<" "<<addCardID<<" "<<addFaceID<<endl;
    PermitInfo* p = new PermitInfo(addName,addIdentity,addCardID,addFaceID);

    for(auto it = permitInfoVector.begin();it!=permitInfoVector.end();++it){
        PermitInfo get = (*it);
        if(get.cardID == addCardID){
            QMessageBox::warning(this,"警告","该卡号已存在,请检查信息是否正确","确定");
            return;
        }
        if(get.faceID.length()>0 && get.faceID == addFaceID){
            QMessageBox::warning(this,"警告","该人脸ID已存在,请检查信息是否正确","确定");
            return;
        }
        if(get == (*p)){
            QMessageBox::warning(this,"警告","该信息已存在","确定");
            return;
        }
    }
    ...
```
同时还要控制输入空间的关系以符合逻辑，例如：
```c++
//addInfo.cpp
//选择身份为学生时禁用"人脸ID"输入框
void AddInfo::on_comboBox_addItentity_activated(const QString &arg1)
{
    if(arg1 == "学生"){
        this->ui->lineEdit_faceID->setText(""); //清空当前内容
        this->ui->lineEdit_faceID->setEnabled(false);

    }
    else if(arg1 == "老师"){
        this->ui->lineEdit_faceID->setEnabled(true);
    }
}
```
### addAccessAction
功能及实现与方法与addInfo类似，这里不再赘述。
## 5. 实验中遇到的问题及解决办法
实验过程中遇到的一个比较的大的问题在于：不同的类需要共享一个数据或者共用一个函数时，发生了multiple definition 的报错  
解决办法：**将共用的变量和函数放在一个.cpp文件中(如这里的globaluse.cpp)，再在globaluse.h中对这些变量和函数进行声明，并注明extern。然后再在需要调用这些变量或者函数的类的头文件中将globaluse.h包含进来即可。**
## 6. 参考资料
1. [解决C++项目编译时的multiple definition of重定义问题](https://blog.csdn.net/maverick1990/article/details/47804973 )   
2. [QT QTableView用法小结](http://blog.sina.com.cn/s/blog_4ba5b45e0102e976.html)  
3. [Qt入门－打开和保存文件对话框](https://blog.csdn.net/xgbing/article/details/7828149)  
4. [截取分割字符串](https://blog.csdn.net/xuleisdjn/article/details/51438162)  
5. [Qt5.6 Documentation](https://doc.qt.io/qt-5.6/index.html)



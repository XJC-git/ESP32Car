package com.xjc.esp32controller;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.SeekBar;
import android.widget.TextView;

import com.xjc.esp32controller.databinding.FragmentControllerBinding;
import com.xjc.esp32controller.databinding.FragmentFirstBinding;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;


public class ControllerFragment extends Fragment implements SensorEventListener {



    public ControllerFragment() throws SocketException {
        // Required empty public constructor
    }

    private TextView gyroscope;
    private SensorManager mSensorMgr;// 声明一个传感管理器对象
    private float mTimestamp; // 记录上次的时间戳

    private FragmentControllerBinding binding;

    private float mAngle[] = new float[3]; // 记录xyz三个方向上的旋转角度
    private static final float NS2S = 1.0f / 1000000000.0f; // 将纳秒转化为秒

    private DatagramSocket sendSocket;
    private InetAddress addr;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        try {
            sendSocket = new DatagramSocket();
            addr = InetAddress.getByName("192.168.31.36");
        } catch (SocketException | UnknownHostException e) {
            throw new RuntimeException(e);
        }

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        binding = FragmentControllerBinding.inflate(inflater, container, false);
        gyroscope = binding.gyroscope;
        binding.reset.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mAngle = new float[3];
            }
        });
        SeekBar depth = binding.depth;
        binding.accelerate.setOnTouchListener((view, motionEvent) -> {
            byte[] buf = new byte[10];
            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN){
                buf=String.format("w-%f",(float)depth.getProgress()/100).getBytes();
            }
            else if(motionEvent.getAction() == MotionEvent.ACTION_UP){
                buf="w-stop".getBytes();
            }
            else{
                return false;
            }

            DatagramPacket outPacket = new DatagramPacket(buf, buf.length,addr, 48975);
            Thread thread = new Thread(new Runnable() {
                @Override
                public void run() {
                    try  {
                        sendSocket.send(outPacket);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
            thread.start();
            return false;
        });
        binding.brake.setOnTouchListener((view, motionEvent) -> {
            byte[] buf = new byte[10];
            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN){
                buf=String.format("s-%f",0.3).getBytes();
            }
            else if(motionEvent.getAction() == MotionEvent.ACTION_UP){
                buf="s-stop".getBytes();
            }
            else{
                return false;
            }

            DatagramPacket outPacket = new DatagramPacket(buf, buf.length,addr, 48975);
            Thread thread = new Thread(new Runnable() {
                @Override
                public void run() {
                    try  {
                        sendSocket.send(outPacket);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
            thread.start();
            return false;
        });
        // 从系统服务中获取传感管理器对象
        mSensorMgr = (SensorManager) this.getActivity().getSystemService(Context.SENSOR_SERVICE);
        return binding.getRoot();
    }

    private float previousAngle = 0;
    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE) { // 陀螺仪角度变更事件
            if (mTimestamp != 0) {
                final float dT = (event.timestamp - mTimestamp) * NS2S;
                mAngle[0] += event.values[0] * dT;
                mAngle[1] += event.values[1] * dT;
                mAngle[2] += event.values[2] * dT;
                float angleZ = (float) Math.toDegrees(mAngle[2]);
                //String desc = String.format("陀螺仪检测方向的转动角度为%.2f", angleZ);
                //gyroscope.setText(desc);
                if(Math.abs(previousAngle-angleZ)>1){
                    if(sendSocket!=null){
                        float targetPWM = (float) (0.075 + (angleZ/40)*0.015);
                        byte[] buf=String.format("%s-%f",angleZ>0?"a":"d",targetPWM).getBytes();
                        DatagramPacket outPacket = new DatagramPacket(buf, buf.length,addr, 48975);
                        Thread thread = new Thread(new Runnable() {
                            @Override
                            public void run() {
                                try  {
                                    sendSocket.send(outPacket);
                                } catch (Exception e) {
                                    e.printStackTrace();
                                }
                            }
                        });
                        thread.start();

                    }
                }
                previousAngle = angleZ;
            }
            mTimestamp = event.timestamp;
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }

    @Override
    public void onPause() {
        super.onPause();
        // 注销当前活动的传感监听器
        mSensorMgr.unregisterListener(this);
    }

    @Override
    public void onResume() {
        super.onResume();
        //注册感光器
        mSensorMgr.registerListener(this,
                mSensorMgr.getDefaultSensor(Sensor.TYPE_GYROSCOPE),
                SensorManager.SENSOR_DELAY_NORMAL);
    }

}
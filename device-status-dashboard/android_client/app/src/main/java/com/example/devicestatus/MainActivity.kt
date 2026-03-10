package com.example.devicestatus

import android.app.AppOpsManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Process
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnPermissions = findViewById<Button>(R.id.btnPermissions)
        val btnStart = findViewById<Button>(R.id.btnStart)
        val btnStop = findViewById<Button>(R.id.btnStop)

        btnPermissions.setOnClickListener {
            // Request Usage Access
            startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
            // Request display over other apps or others if needed
        }

        btnStart.setOnClickListener {
            val serviceIntent = Intent(this, StatusService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent)
            } else {
                startService(serviceIntent)
            }
            findViewById<TextView>(R.id.tvStatus).text = "Status: Running"
        }

        btnStop.setOnClickListener {
            stopService(Intent(this, StatusService::class.java))
            findViewById<TextView>(R.id.tvStatus).text = "Status: Stopped"
        }
    }

    override fun onResume() {
        super.onResume()
        checkPermissions()
    }

    private fun checkPermissions() {
        val appOps = getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
        val mode = appOps.checkOpNoThrow(
            AppOpsManager.OPSTR_GET_USAGE_STATS,
            Process.myUid(),
            packageName
        )
        if (mode == AppOpsManager.MODE_ALLOWED) {
            findViewById<Button>(R.id.btnPermissions).text = "Permission Granted ✓"
            findViewById<Button>(R.id.btnPermissions).isEnabled = false
        }
    }
}

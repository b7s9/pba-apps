import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Component, OnInit } from '@angular/core';
import { Device, DeviceInfo } from '@capacitor/device';
import { Geolocation, Position } from '@capacitor/geolocation';
import { Network } from '@capacitor/network';


@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit {

  online: boolean | null = null;
  deviceInfo: DeviceInfo | null = null;
  geoPerms: boolean | null = null;

  violationImage: string | undefined | null = null;
  violationPosition: Position | null = null;
  violationTime: Date | null = null;

  constructor() {}

  async getCurrentPosition() {
    Geolocation.getCurrentPosition({enableHighAccuracy: true, maximumAge: 30000})
    .then(
      (coordinates) => {
        this.violationPosition = coordinates;
        this.geoPerms = true;
      }
    );
  }

  async takePicture() {
    this.getCurrentPosition();

    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.Uri,
      source: CameraSource.Camera,
      webUseInput: true
    });

    this.violationImage = image.webPath;
    this.violationTime = new Date();
  }

  async submit() {
    this.violationImage = null;
    this.violationPosition = null;
  }

  requestGeoPerms = () => {
    if ( Capacitor.isNativePlatform() ){
      Geolocation.requestPermissions();
    } else {
      this.getCurrentPosition();
    }
    this.checkPermission();
  }

  checkPermission = async () => {
    if ( Capacitor.isNativePlatform() ){
      try {
        const status = await Geolocation.checkPermissions();
        if (status) {
          this.geoPerms = true;
        }
        this.geoPerms = false;
      } catch(e) {
        console.log(e);
        this.geoPerms = false;
      }
    } else {
      navigator.permissions.query({ name: "geolocation" }).then((result) => {
        if (result.state === "granted") {
          this.geoPerms = true;
        } else if (result.state === "prompt") {
          if (this.deviceInfo !== null && this.deviceInfo.operatingSystem === "ios") {
            this.geoPerms = true;
          } else {
            this.geoPerms = false;
          }
        } else {
          this.geoPerms = false;
        }
      });
    }
  }

  ngOnInit(): void {
    Device.getInfo().then((deviceInfo) => {
      this.deviceInfo = deviceInfo;
      Network.getStatus().then((connectionStatus) => {
        this.online = connectionStatus.connected;
      });
      Network.addListener('networkStatusChange', connectionStatus => {
        this.online = connectionStatus.connected;
      });
      this.checkPermission();
    });
  }

}

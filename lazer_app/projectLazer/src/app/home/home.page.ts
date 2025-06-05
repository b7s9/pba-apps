import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Component, OnInit } from '@angular/core';
import { Device, DeviceInfo } from '@capacitor/device';
import { Geolocation, Position } from '@capacitor/geolocation';
import { LoadingController } from '@ionic/angular';
import { Network } from '@capacitor/network';


async function compressJpegDataUrl(dataUrl: string, quality: number): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error("Canvas context not available"));
        return;
      }
      ctx.drawImage(img, 0, 0);
      const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
      resolve(compressedDataUrl);
    };
    img.onerror = (error) => {
        reject(error);
    }
    img.src = dataUrl;
  });
}

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

  lastImage: string | undefined | null = null;
  lastPosition: Position | null = null;
  lastTime: Date | null = null;
  lastViolationData: any = null;

  constructor(
    private loadingCtrl: LoadingController,
  ) {}

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
    this.violationImage = null;
    this.violationPosition = null;
    this.violationTime = null;
    this.getCurrentPosition();

    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera,
      webUseInput: true
    });

    this.violationImage = image.dataUrl;
    this.violationTime = new Date();
  }

  async submit() {

    function submitData (lat: number, long: number, dt: Date, img: string): Promise<any> {
      return new Promise((resolve, reject) => {
        let request = new XMLHttpRequest();
        request.addEventListener("readystatechange", () => {
          if (request.readyState === 4 && request.status === 200) {
            let data = JSON.parse(request.responseText);
            resolve(data);
          } else if (request.readyState === 4) {
            reject("error getting resources");
          }
        });

        compressJpegDataUrl(img, .3).then((newImg) => {
          const formData = new FormData();
          formData.append("latitude", JSON.stringify(lat));
          formData.append("longitude", JSON.stringify(long));
          formData.append("datetime", dt.toISOString());
          formData.append("image", newImg);

          request.open("POST", "https://bikeaction.ngrok.io/lazer/submit/");
          request.send(formData);
        });
      });
    }

    if (
      this.violationImage !== null &&
      this.violationTime !== null &&
      this.violationPosition !== null
    ) {
      this.loadingCtrl.create({
        message: 'Processing...',
        duration: 20000,
      }).then((loader) => {
        loader.present();
        submitData(
          this.violationPosition!.coords!.latitude,
          this.violationPosition!.coords!.longitude,
          this.violationTime!,
          this.violationImage!
        )
        .then((data: any) => {
          this.lastViolationData = data;
          console.log(data);
          this.lastImage = this.violationImage;
          this.lastTime = this.violationTime
          this.lastPosition = this.violationPosition;
          this.violationPosition = null;
          this.violationTime = null;
          this.violationImage = null;
          setTimeout(() => {loader.dismiss()}, 100);
        })
        .catch((err: any) => {
          console.log(err);
          setTimeout(() => {loader.dismiss()}, 100);
        });
      });
    }

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

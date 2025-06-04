import torch
import torch.nn as nn
import torch.nn.functional as F

class UNetFlexible(nn.Module):
    def __init__(self, base_channels=64):
        super(UNetFlexible, self).__init__()

        # Encoder
        self.enc1 = self.conv_block(1, base_channels)
        self.enc2 = self.conv_block(base_channels, base_channels * 2)
        self.enc3 = self.conv_block(base_channels * 2, base_channels * 4)

        self.pool = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = self.conv_block(base_channels * 4, base_channels * 8)

        # Decoder
        self.up3 = self.up_block(base_channels * 8, base_channels * 4)
        self.up2 = self.up_block(base_channels * 4 * 2, base_channels * 2)
        self.up1 = self.up_block(base_channels * 2 * 2, base_channels)

        # Final layer
        self.final_conv = nn.Conv2d(base_channels * 2, 2, kernel_size=1)  # 2 channels for (x, y) offsets

    def conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def up_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))

        b = self.bottleneck(self.pool(e3))

        d3 = self.up3(b)
        e3 = F.interpolate(e3, size=d3.shape[2:], mode='bilinear', align_corners=True)
        d3 = torch.cat([d3, e3], dim=1)

        d2 = self.up2(d3)
        e2 = F.interpolate(e2, size=d2.shape[2:], mode='bilinear', align_corners=True)
        d2 = torch.cat([d2, e2], dim=1)

        d1 = self.up1(d2)
        e1 = F.interpolate(e1, size=d1.shape[2:], mode='bilinear', align_corners=True)
        d1 = torch.cat([d1, e1], dim=1)

        out = self.final_conv(d1)
        out = F.interpolate(out, size=x.shape[2:], mode='bilinear', align_corners=True)

        return out
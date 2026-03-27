from mcpi.minecraft import Minecraft
from mcpi.minecraft import Vec3
from mcpi import block
import time

def clamp(v,limit):
    if v > limit: return limit
    if v < -limit: return -limit
    return v

def limit_vec(v, max_len):
    length = (v.x**2 + v.y**2 + v.z**2)**0.5
    if length > max_len:
        s = max_len / length
        return Vec3(v.x*s, v.y*s, v.z*s)
    return v

#def snap_to_ground(y):
    #for dy in range(20):
        #new_y = y + 10 -dy
        #block = mc.getBlock(int(pos.x),int(new_y),int(pos.z))
        #if block != 0:
            #return new_y
    #return y

if __name__=="__main__":

    mc = Minecraft.create()
    id_list = mc.getPlayerEntityIds()
    id1 = id_list[0]
    id2 = id_list[1]
    mc.camera.setFollow(id1)

    # parameters of PID
    Kp = 0.2
    Ki = 0.05
    Kd = 0.1

    integral = Vec3(0,0,0)
    prev_error = Vec3(0,0,0)
    derivative = Vec3(0,0,0)

    dt = 0.05
    integral_limit = 5
    output_limit = 0.3

    while True:
        pos = mc.entity.getPos(id1)
        target = mc.entity.getPos(id2)
        error = Vec3(
            target.x - pos.x,
            target.y - pos.y,
            target.z - pos.z
        )

        # I
        integral.x += error.x * dt
        integral.y += error.y * dt
        integral.z += error.z * dt
        integral.x = clamp(integral.x, integral_limit)
        integral.y = clamp(integral.y, integral_limit)
        integral.z = clamp(integral.z, integral_limit)

        # D
        derivative.x = (error.x - prev_error.x) / dt
        derivative.y = (error.y - prev_error.y) / dt
        derivative.z = (error.z - prev_error.z) / dt

        # PID
        d_deplacement = Vec3(0,0,0)
        d_deplacement.x = Kp * error.x + Ki * integral.x + Kd * derivative.x
        d_deplacement.y = Kp * error.y + Ki * integral.y + Kd * derivative.y
        d_deplacement.z = Kp * error.z + Ki * integral.z + Kd * derivative.z

        # limit
        d_deplacement = limit_vec(d_deplacement, output_limit)

        mc.entity.setPos(id1, pos.x + d_deplacement.x, pos.y + d_deplacement.y, pos.z + d_deplacement.z)

        print(f"error_x={error.x:.2f} error_y={error.y:.2f} error_z={error.z:.2f}")

        prev_error = Vec3(error.x, error.y, error.z)
        time.sleep(dt)
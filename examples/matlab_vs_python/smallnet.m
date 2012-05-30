clear all;

tic;

% Created by Eugene M. Izhikevich, 2003 Modified by S. Fusi 2007
% Excitatory neurons   Inhibitory neurons
Ne=1000;                Ni=4;
Je=250/Ne; % synaptic couplings
Ji=0;

reset=0; refr=2.5; % reset depolarization (mV) and refractory period (ms)
connectivity=[heaviside(rand(Ne+Ni,Ne)-.9),heaviside(rand(Ne+Ni,Ni)-.9)]; % connectivity matrix
S=[Je*rand(Ne+Ni,Ne),-Ji*rand(Ne+Ni,Ni)]; % synaptic couplings (mV)
S=S.*connectivity;

lambda=5;  % leakage (mV/ms)
dt=.05; sdt=sqrt(dt); 
mb=3; sb=4; % statistics of the background external current
mue=mb; sigmae=sb;
sigmai=0.0

v=0.*ones(Ne+Ni,1);  % Initial values of v
r=0.*zeros(Ne+Ni,1); % refractory periods
firings=[];           % spike timings

disp(sprintf('mu(nu=5Hz)=%f\n',mb+Ne*Je*.015-lambda));
disp(sprintf('mu(nu=100Hz)=%f\n',mb+Ne*Je*.1-lambda));

toc;
tic;

duration=400; % total duration of the simulation (ms)
ti=1;
for t=1:dt:duration
   if(t>150) % activate a strong external input
     mue=6.5; 
     sigmae=7.5;
   end

   if(t>300) % restore the initial statistics of the external current
     mue=mb; 
     sigmae=sb; 
   end
      
   Iext=[sigmae*randn(Ne,1);sigmai*randn(Ni,1)]; % external input
   fired=find(v>=20); % indices of spikes
   if ~isempty(fired)      
      firings=[firings; t+0*fired, fired];     
      v(fired)=reset;
      r(fired)=refr;
      aux=v-dt*(lambda-mue)+sum(S(:,fired),2)+sdt*Iext;
   else
      aux=v-dt*(lambda-mue)+sdt*Iext;     
   end
   nr=find(r<=0); % neurons which are not in the refractory period
   v(nr)=heaviside(aux(nr)).*aux(nr);
   nr=find(r>0);
   r(nr)=r(nr)-dt;
   vt(ti)=v(1); tt(ti)=t;
   ti=ti+1;
end;

toc;

% -------------------------------------------------------------------------
% Plot everything
% -------------------------------------------------------------------------

disp('Plotting...')

tic;

figure(1);

subplot(3,1,1);
vt(find(vt>=20))=65;
plot(tt,vt);
ylabel('V-V_{rest} (mV)');

subplot(3,1,2);
if Ne<100
ie=find(firings(:,2)<=Ne);
else
ie=find(firings(:,2)<=100);
end  
plot(firings(ie,1),firings(ie,2),'.');
set(gca,'xlim',[0 duration]);
ylabel('Neuron index');

subplot(3,1,3);
k=1;
binsize=1;
for tbins=1:binsize:(duration-binsize)
m(k)=size(find((firings(:,2)<=Ne) & (firings(:,1)>=tbins) & (firings(:,1)<tbins+binsize)),1);
time(k)=tbins+binsize/2;
k=k+1;
end
h=plot(time,m/Ne/binsize*1000.); set(h,'linewidth',2);
ma=mean(m(find(time>40))/Ne/binsize*1000.);
line([0 duration],[ma ma]);
h=line([20 20],[0 50]); set(h,'linestyle','--');

ylabel('Hz');
xlabel('time (ms)');

toc;
